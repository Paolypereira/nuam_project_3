# mercados/utils_import.py
import os, re, unicodedata
from datetime import datetime
import pandas as pd
from .models import Empresa, Pais

# ------------------ helpers ------------------

def _norm(s):
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip().lower()

def _find_header_row(raw: pd.DataFrame, scan_limit=200):
    """
    Busca fila candidata a encabezado dentro de las primeras `scan_limit`.
    Criterio: contenga 2+ palabras clave y >=3 celdas no vacías.
    """
    keywords = ["nemo", "ticker", "emisor", "nombre", "cap", "capital", "bursatil", "market"]
    m = min(scan_limit, len(raw))
    for i in range(m):
        vals = [_norm(v) for v in list(raw.iloc[i].values)]
        score = sum(any(k in val for k in keywords) for val in vals)
        nonempty = sum(1 for val in vals if val)
        if score >= 2 and nonempty >= 3:
            return i
    # Fallback: primera fila con >=3 celdas no vacías
    for i in range(m):
        vals = [_norm(v) for v in list(raw.iloc[i].values)]
        if sum(1 for v in vals if v) >= 3:
            return i
    return 0

def _combine_two_header_rows(raw: pd.DataFrame, header_row: int):
    """
    Si hay 2 filas de encabezado consecutivas, combínalas.
    """
    cols1 = list(raw.iloc[header_row].fillna("").astype(str))
    cols2 = list(raw.iloc[header_row+1].fillna("").astype(str)) if header_row+1 < len(raw) else [""] * len(cols1)
    out = []
    for a, b in zip(cols1, cols2):
        a = a.strip(); b = b.strip()
        if a and b and _norm(a) != _norm(b):
            out.append(f"{a} {b}")
        else:
            out.append(a or b)
    return out

# ------------------ importador principal ------------------

def import_empresas_from_excel(path: str):
    """
    Lee un Excel NUAM en formato ancho con 3 bloques (BCS/bvc/BVL):
      [Emisor] [Ticker] [Cap]   [Emisor] [Ticker] [Cap]   [Emisor] [Ticker] [Cap]
    Detecta encabezados, identifica índices por bolsa y crea/actualiza Empresas.
    Asigna país/moneda por defecto según la bolsa.
    """
    if not os.path.exists(path):
        return {"ok": False, "msg": f"No existe el archivo: {path}"}

    try:
        xls = pd.ExcelFile(path)
    except Exception as e:
        return {"ok": False, "msg": f"Error leyendo Excel: {e}"}

    # probar primero hojas tipo 'Nemo ... Cap'
    sheets = sorted(xls.sheet_names, key=lambda s: (0 if ("Nemo" in s and "Cap" in s) else 1, s))

    created = updated = skipped = 0
    used_sheet = None

    # Mapeo por bolsa -> país / moneda
    bolsa_meta = {
        "bcs": {"pais": "CHL", "moneda": "CLP"},
        "bvc": {"pais": "COL", "moneda": "COP"},
        "bvl": {"pais": "PER", "moneda": "PEN"},
    }

    for sheet in sheets:
        # 1) Crudo + detección encabezado
        try:
            raw = pd.read_excel(path, sheet_name=sheet, header=None, engine="openpyxl")
        except Exception:
            continue

        header_row = _find_header_row(raw, scan_limit=200)

        # 2) Intento A (header_row)
        try:
            dfA = pd.read_excel(path, sheet_name=sheet, header=header_row, engine="openpyxl").dropna(how="all")
            colsA = list(dfA.columns); colsA_norm = [_norm(c) for c in colsA]
        except Exception:
            dfA = None; colsA = []; colsA_norm = []

        # 3) Intento B (combinar 2 encabezados)
        try:
            combined = _combine_two_header_rows(raw, header_row)
            dfB = pd.read_excel(path, sheet_name=sheet, header=header_row+1, engine="openpyxl").dropna(how="all")
            if dfB is not None and len(dfB.columns) == len(combined):
                dfB.columns = combined
            colsB = list(dfB.columns); colsB_norm = [_norm(c) for c in colsB]
        except Exception:
            dfB = None; colsB = []; colsB_norm = []

        # Elegir la versión con más señales (preferimos B si existe)
        useB = dfB is not None and any("ticker" in c and ("bcs" in c or "bvc" in c or "bvl" in c) for c in colsB_norm)
        df = dfB if useB else dfA
        cols = colsB if useB else colsA
        cols_norm = colsB_norm if useB else colsA_norm
        if df is None:
            continue

        # ---------- Identificar índices por bolsa ----------
        # Buscamos, para cada bolsa, el índice del Ticker y de la Cap dentro del bloque.
        blocks = {}  # ej: {"bcs": {"ticker": idx, "cap": idx, "emisor": idx}}
        for bolsa in ["bcs", "bvc", "bvl"]:
            # Ticker: columna que contenga 'ticker' y el nombre de la bolsa
            t_idx = next((i for i, c in enumerate(cols_norm) if "ticker" in c and bolsa in c), None)
            # Cap: preferimos la columna contigua con "cap" (suele estar a +1)
            c_idx = None
            if t_idx is not None:
                # primero probar +1 y +2, luego cualquier columna con cap y esa bolsa
                for k in (t_idx + 1, t_idx + 2):
                    if 0 <= k < len(cols_norm) and ("cap" in cols_norm[k] or "capital" in cols_norm[k]):
                        c_idx = k; break
                if c_idx is None:
                    c_idx = next((i for i, c in enumerate(cols_norm) if ("cap" in c or "capital" in c) and bolsa in c), None)

            # Emisor: suele estar justo antes del ticker
            e_idx = None
            if t_idx is not None:
                cand = t_idx - 1
                if 0 <= cand < len(cols_norm) and ("emisor" in cols_norm[cand] or "issuer" in cols_norm[cand] or "nombre" in cols_norm[cand]):
                    e_idx = cand
                else:
                    # fallback: busca el 'emisor' más cercano a la izquierda
                    for k in range(t_idx - 1, max(-1, t_idx - 4), -1):
                        if 0 <= k < len(cols_norm) and ("emisor" in cols_norm[k] or "issuer" in cols_norm[k] or "nombre" in cols_norm[k]):
                            e_idx = k; break

            if t_idx is not None or e_idx is not None or c_idx is not None:
                blocks[bolsa] = {"ticker": t_idx, "cap": c_idx, "emisor": e_idx}

        # Si no encontramos ningún bloque, intentar fallback genérico
        if not blocks:
            continue

        # ---------- Procesar filas: hasta 3 empresas por fila ----------
        for _, r in df.iterrows():
            for bolsa, idxs in blocks.items():
                t_i, e_i, c_i = idxs.get("ticker"), idxs.get("emisor"), idxs.get("cap")
                # al menos ticker o nombre debe existir
                ticker = str(r.iloc[t_i]).strip() if (t_i is not None and pd.notna(r.iloc[t_i])) else ""
                nombre = str(r.iloc[e_i]).strip() if (e_i is not None and pd.notna(r.iloc[e_i])) else ""

                if not ticker and not nombre:
                    continue  # nada que crear

                # si falta ticker pero hay nombre, generamos uno simple (no ideal, pero evita perder el registro)
                if not ticker and nombre:
                    ticker = re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", nombre).upper())[:10]

                # capitalización
                cap = None
                if c_i is not None and pd.notna(r.iloc[c_i]):
                    try:
                        cap = float(str(r.iloc[c_i]).replace(",", "").replace(" ", ""))
                    except Exception:
                        cap = None

                # país/moneda por defecto según bolsa
                meta = bolsa_meta[bolsa]
                pais_codigo = meta["pais"]
                moneda_def = meta["moneda"]
                pais_obj = Pais.objects.filter(codigo=pais_codigo).first()

                defaults = {
                    "nombre": nombre or None,
                    "pais": pais_obj,
                    "sector": None,  # el Excel no lo trae; puedes poblarlo después
                    "moneda": moneda_def,
                    "capitalizacion": cap,
                    "mercado": bolsa.upper(),  # BCS / BVC / BVL
                    "fuente": "Excel NUAM",
                    "fecha_reporte": None,
                }

                obj, created_flag = Empresa.objects.update_or_create(ticker=ticker, defaults=defaults)
                if created_flag:
                    created += 1
                else:
                    updated += 1

        used_sheet = sheet
        break  # ya importamos desde esta hoja

    if used_sheet is None:
        return {"ok": False, "msg": "No se identificó ninguna tabla válida (bloques BCS/bvc/BVL)."}

    return {"ok": True, "msg": f"Hoja usada: {used_sheet}. Creadas: {created}, actualizadas: {updated}, omitidas: {skipped}"}
