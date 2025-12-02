from django.core.management.base import BaseCommand
from mercados.models import Empresa, Pais
import pandas as pd, os, re, unicodedata
from datetime import datetime

def norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def find_header_row(raw: pd.DataFrame, scan_limit=200):
    """
    Busca fila candidata a encabezado en las primeras `scan_limit` filas.
    Criterio: que contenga palabras clave de columnas y al menos 3 celdas no vacías.
    """
    targets = ["nemo", "ticker", "emisor", "nombre", "pais", "country", "moneda", "currency", "sector", "market", "cap", "capital"]
    m = min(scan_limit, len(raw))
    for i in range(m):
        vals = [norm(v) for v in list(raw.iloc[i].values)]
        score = sum(any(t in v for t in targets) for v in vals)
        nonempty = sum(1 for v in vals if v)
        if score >= 2 and nonempty >= 3:
            return i
    # Fallback: primera fila con >=3 celdas no vacías
    for i in range(m):
        vals = [norm(v) for v in list(raw.iloc[i].values)]
        if sum(1 for v in vals if v) >= 3:
            return i
    return 0

def combine_two_header_rows(df: pd.DataFrame, header_row: int):
    """
    Si hay encabezados en dos filas consecutivas, combina ambas para formar nombres de columna más expresivos.
    """
    cols1 = list(df.iloc[header_row].fillna("").astype(str))
    cols2 = list(df.iloc[header_row + 1].fillna("").astype(str)) if header_row + 1 < len(df) else [""] * len(cols1)
    combined = []
    for a, b in zip(cols1, cols2):
        a = a.strip()
        b = b.strip()
        if a and b and norm(a) != norm(b):
            combined.append(f"{a} {b}")
        else:
            combined.append(a or b)
    return combined

def pick_col(cols_norm, *candidates):
    cands = [norm(c) for c in candidates]
    for idx, c in enumerate(cols_norm):
        for cand in cands:
            if cand and cand in c:
                return idx
    return None

def try_load_sheet(path: str, sheet_name: str, stdout, stderr):
    # 1) Leer crudo sin header para detectar fila de encabezado (profundo)
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
    header_row = find_header_row(raw, scan_limit=200)

    stdout.write(f"🔎 [{sheet_name}] header_row detectada: {header_row}")

    # 2) Intento A: usar esa fila como header
    dfA = pd.read_excel(path, sheet_name=sheet_name, header=header_row, engine="openpyxl")
    dfA = dfA.dropna(how="all")
    colsA = list(dfA.columns)
    colsA_norm = [norm(c) for c in colsA]

    # 3) Intento B: combinar 2 filas de encabezado (header_row y header_row+1) y re-asignar
    combined_cols = combine_two_header_rows(raw, header_row)
    dfB = pd.read_excel(path, sheet_name=sheet_name, header=header_row+1, engine="openpyxl")
    dfB = dfB.dropna(how="all")
    if len(dfB.columns) == len(combined_cols):
        dfB.columns = combined_cols
    colsB = list(dfB.columns)
    colsB_norm = [norm(c) for c in colsB]

    # función de evaluación de estructura válida
    def evaluate(cols_norm, cols_label):
        idx_ticker = pick_col(cols_norm, "ticker", "nemo", "nemotecnico", "nemotecnico/ticker", "nemotecnico | ticker")
        idx_nombre = pick_col(cols_norm, "nombre emisor", "nombre", "emisor", "issuer", "company")
        idx_pais   = pick_col(cols_norm, "pais", "país", "country")
        idx_sector = pick_col(cols_norm, "sector", "industria")
        idx_moneda = pick_col(cols_norm, "moneda", "currency")
        idx_mcap   = pick_col(cols_norm, "market cap", "cap bursatil", "cap. bursatil", "capitalizacion", "capitalization", "market capitalization")
        idx_fecha  = pick_col(cols_norm, "fecha", "fecha reporte", "date")
        idx_merc   = pick_col(cols_norm, "mercado", "exchange", "bolsa")

        ok = (idx_ticker is not None) and (idx_nombre is not None)
        return ok, dict(
            idx_ticker=idx_ticker, idx_nombre=idx_nombre, idx_pais=idx_pais, idx_sector=idx_sector,
            idx_moneda=idx_moneda, idx_mcap=idx_mcap, idx_fecha=idx_fecha, idx_merc=idx_merc,
            cols_label=cols_label
        )

    okA, mapA = evaluate(colsA_norm, "A")
    okB, mapB = evaluate(colsB_norm, "B")

    # Preferir el que tenga mapeo válido
    if okB:
        return dfB, mapB
    if okA:
        return dfA, mapA

    # Ninguno válido: log diagnóstico
    stderr.write(f"❌ [{sheet_name}] No se identificaron columnas mínimas.\n"
                 f"    Cols A: {colsA}\n"
                 f"    Cols B: {colsB}\n")
    return None, None

class Command(BaseCommand):
    help = "Importa empresas desde el Excel de NUAM (detecta hoja/encabezados/columnas automáticamente)."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default="Informe_Bursátil_Regional_2025-08.xlsx")

    def handle(self, *args, **opts):
        path = opts["file"]
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f"No se encontró: {path}"))
            return

        xls = pd.ExcelFile(path)
        self.stdout.write(self.style.NOTICE(f"📚 Hojas detectadas: {xls.sheet_names}"))

        # Priorizamos la 'Nemo...' pero probamos todas si falla
        sheet_order = sorted(xls.sheet_names, key=lambda s: (0 if ("Nemo" in s and "Cap" in s) else 1, s))

        df = None
        mapping = None
        used_sheet = None
        for sheet in sheet_order:
            self.stdout.write(self.style.NOTICE(f"🧪 Probando hoja: {sheet}"))
            dfi, mapi = try_load_sheet(path, sheet, self.stdout, self.stderr)
            if dfi is not None:
                df, mapping, used_sheet = dfi, mapi, sheet
                break

        if df is None:
            self.stderr.write(self.style.ERROR("No se pudo encontrar una tabla con 'ticker/nemo' y 'nombre/emisor'."))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ Usando hoja: {used_sheet} (modo {mapping['cols_label']})"))
        cols = list(df.columns)
        self.stdout.write(self.style.NOTICE(f"🧱 Columnas finales: {cols}"))

        # Mapeo de índices
        idx_ticker = mapping["idx_ticker"]
        idx_nombre = mapping["idx_nombre"]
        idx_pais   = mapping["idx_pais"]
        idx_sector = mapping["idx_sector"]
        idx_moneda = mapping["idx_moneda"]
        idx_mcap   = mapping["idx_mcap"]
        idx_fecha  = mapping["idx_fecha"]
        idx_merc   = mapping["idx_merc"]

        created = updated = skipped = 0

        for _, row in df.iterrows():
            def get(idx):
                if idx is None: return None
                val = row.iloc[idx]
                return None if pd.isna(val) else val

            ticker = str(get(idx_ticker) or "").strip()
            nombre = str(get(idx_nombre) or "").strip()
            if not ticker or not nombre:
                skipped += 1
                continue

            # País
            pais_obj = None
            pv = str(get(idx_pais) or "").strip()
            if pv:
                pais_obj = Pais.objects.filter(codigo__iexact=pv).first() or \
                           Pais.objects.filter(nombre__iexact=pv).first()

            # Capitalización
            cap_val = None
            cv = get(idx_mcap)
            if cv is not None:
                try:
                    cap_val = float(str(cv).replace(",", "").replace(" ", ""))
                except:
                    cap_val = None

            # Fecha
            fecha_val = None
            fv = get(idx_fecha)
            if fv is not None:
                try:
                    fecha_val = fv.date() if hasattr(fv, "date") else datetime.fromisoformat(str(fv)[:10]).date()
                except:
                    fecha_val = None

            defaults = {
                "nombre": nombre,
                "pais": pais_obj,
                "sector": (str(get(idx_sector)).strip() or None) if get(idx_sector) is not None else None,
                "moneda": (str(get(idx_moneda)).strip() or None) if get(idx_moneda) is not None else None,
                "capitalizacion": cap_val,
                "mercado": (str(get(idx_merc)).strip() or None) if get(idx_merc) is not None else None,
                "fuente": "Excel NUAM",
                "fecha_reporte": fecha_val,
            }

            obj, is_created = Empresa.objects.update_or_create(ticker=ticker, defaults=defaults)
            created += 1 if is_created else 0
            updated += 0 if is_created else 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Empresas creadas: {created}, actualizadas: {updated}, omitidas: {skipped}"
        ))
