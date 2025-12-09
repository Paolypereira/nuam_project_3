from django.shortcuts import render, redirect
from django.db.models import F
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
from .models import Empresa, empresa_a_dict
from kafka_service import publicar_evento_empresa
from .forms import SignupForm, UserUpdateForm
from .models import Pais, Empresa
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render

def dashboard_monedas(request):
    return render(request, "dashboard_monedas.html")
from .serializers import PaisSerializer, EmpresaSerializer


def home(request):
    return render(request, "home.html", {
        "title": "NUAM - Mantenedor & API",
        "links": {
            "catalogo": "/catalogo/",
            "admin": "/admin/",
            "mer": "/mer/",
            "convertidor": "/convertir-moneda/",
        }
    })
from django.http import JsonResponse
import requests

def datos_dashboard_monedas(request):
    base = request.GET.get("base", "USD")  # "USD", "CLP", "COP", "PEN", "UF"
    try:
        periodo = int(request.GET.get("periodo", "7"))
    except ValueError:
        periodo = 7

    url = "https://api.exchangerate-api.com/v4/latest/USD"
    r = requests.get(url, timeout=5)
    data = r.json()
    rates = data.get("rates", {})

    # Códigos reales en la API
    monedas = ["CLP", "COP", "PEN", "CLF"]  # CLF = UF en la API

    labels = []
    valores = []
    valores_para_ranking = {}

    # ---- comparación actual, respetando la base elegida ----
    for m in monedas:
        if m in rates:
            etiqueta = "UF" if m == "CLF" else m
            labels.append(etiqueta)

            # valor de 1 unidad de esa moneda en USD
            valor_usd = 1 / rates[m]

            # moneda base elegida por el usuario
            base_code = "CLF" if base == "UF" else base
            if base_code == "USD":
                valor = valor_usd
            elif base_code in rates:
                # valor de 1 unidad de la base en USD
                valor_base_usd = 1 / rates[base_code]
                # cuánto vale 1 unidad de m en unidades de la base
                valor = valor_usd / valor_base_usd
            else:
                # si la base no existe en la API, caer a USD
                valor = valor_usd

            valor_red = round(valor, 4)
            valores.append(valor_red)
            valores_para_ranking[etiqueta] = valor_red

    # ---- histórico simulado (solo cambia etiqueta de base) ----
    labels_hist = [f"Día {i}" for i in range(1, periodo + 1)]
    colores = {
        "CLP": "#4e79a7",
        "COP": "#f28e2b",
        "PEN": "#e15759",
        "CLF": "#76b7b2",
    }
    series = []
    for m in monedas:
        if m in rates:
            base_val = 1 / rates[m]  # valor en USD, solo para forma de la curva
            puntos = []
            for i in range(periodo):
                factor = 1 + (i - periodo / 2) * 0.005
                puntos.append(round(base_val * factor, 4))
            series.append({
                "label": f"{'UF' if m=='CLF' else m} vs {base}",
                "data": puntos,
                "borderColor": colores[m],
                "fill": False,
                "tension": 0.2,
            })

    max_moneda = min_moneda = None
    if valores_para_ranking:
        max_moneda = max(valores_para_ranking, key=valores_para_ranking.get)
        min_moneda = min(valores_para_ranking, key=valores_para_ranking.get)

    return JsonResponse({
        "base": base,
        "labels": labels,
        "valores": valores,
        "labels_historico": labels_hist,
        "series": series,
        "fecha": data.get("date"),
        "max_moneda": max_moneda,
        "min_moneda": min_moneda,
    })

# -------- DIAGRAMA NUAM (M.E.R.) --------
def mer_view(request):
    return render(request, "mer.html", {
        "title": "Diagrama NUAM (M.E.R.)"
    })


# -------- VISTA HTML DEL CONVERTIDOR --------
def convertidor_view(request):
    return render(request, "convertidor.html", {
        "title": "Convertidor de Moneda"
    })


# -------- API convertidor de moneda (JSON) --------
def convertir_moneda(request):
    # Validar monto
    monto_str = request.GET.get("monto", "").strip()
    if not monto_str:
        return JsonResponse({"error": "Debe indicar un monto numérico"}, status=400)
    try:
        monto = float(monto_str)
    except ValueError:
        return JsonResponse({"error": "El monto debe ser un número válido"}, status=400)

    moneda = request.GET.get("moneda", "CLP")  # CLP, PEN, COP, etc.

    # Llamar API externa con manejo de errores
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        return JsonResponse(
            {"error": "No se pudo contactar la API de tipo de cambio"},
            status=502,
        )

    rates = data.get("rates", {})
    if moneda not in rates:
        return JsonResponse(
            {"error": f"Moneda no soportada: {moneda}"},
            status=400,
        )

    tasa_moneda = rates[moneda]
    usd_por_moneda = 1 / tasa_moneda
    resultado = monto * usd_por_moneda

    return JsonResponse(
        {
            "monto": monto,
            "moneda": moneda,
            "resultado_usd": round(resultado, 4),
            "usd_por_moneda": usd_por_moneda,
            "fecha": data.get("date"),
            "tasa_base": "USD",
        }
    )

# -------- API REST principal (DRF con paginación) --------
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["ticker", "nombre", "pais__codigo", "sector", "moneda", "mercado"]
    ordering_fields = ["ticker", "nombre", "capitalizacion"]
    ordering = ["ticker"]
    lookup_field = "ticker"

    filterset_fields = {
        "pais__codigo": ["exact", "in"],
        "moneda": ["exact", "in"],
        "sector": ["exact"],
    }


class PaisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    lookup_field = "codigo"


class TopEmpresasPorPais(APIView):
    def get(self, request):
        pais = request.GET.get("pais")
        try:
            n = int(request.GET.get("n", 5))
        except ValueError:
            n = 5

        qs = Empresa.objects.all()
        if pais:
            qs = qs.filter(pais__codigo__iexact=pais)

        qs = qs.order_by(F("capitalizacion").desc(nulls_last=True))[:n]

        data = [
            {
                "ticker": e.ticker,
                "nombre": e.nombre,
                "pais": e.pais.codigo if e.pais else None,
                "capitalizacion": float(e.capitalizacion) if e.capitalizacion is not None else None,
                "moneda": e.moneda,
            }
            for e in qs
        ]
        return Response({"pais": pais, "n": n, "resultados": data})


# -------- Endpoint SIN paginación para el front /catalogo-data/ --------
@api_view(["GET"])
def empresas_sin_paginacion(request):
    qs = (
        Empresa.objects
        .all()
        .order_by("ticker")
        .values(
            "ticker",
            "nombre",
            "moneda",
            "capitalizacion",
            "pais__codigo",
        )
    )

    data = [
        {
            "ticker": row["ticker"],
            "nombre": row["nombre"],
            "pais": row["pais__codigo"],
            "moneda": row["moneda"],
            "capitalizacion": float(row["capitalizacion"]) if row["capitalizacion"] is not None else None,
        }
        for row in qs
    ]

    return Response(data)


# -------- Registro y CRUD de cuenta de usuario --------
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "cuenta/registro.html", {"form": form})


@login_required
def mi_cuenta(request):
    return render(request, "cuenta/micuenta.html", {"user": request.user})


@login_required
def editar_cuenta(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("mi-cuenta")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "cuenta/editar_cuenta.html", {"form": form})


@login_required
def eliminar_cuenta(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        return redirect("home")
    return render(request, "cuenta/eliminar_cuenta.html")

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)
def convertir_moneda(request):
    monto_str = request.GET.get("monto", "").strip()
    if not monto_str:
        logger.warning("Intento de conversión sin monto")
        return JsonResponse({"error": "Debe indicar un monto numérico"}, status=400)
    try:
        monto = float(monto_str)
    except ValueError:
        logger.warning("Monto inválido: %s", monto_str)
        return JsonResponse({"error": "El monto debe ser un número válido"}, status=400)

    moneda = request.GET.get("moneda", "CLP")

    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        logger.error("Fallo al llamar API de tipo de cambio", exc_info=True)
        return JsonResponse(
            {"error": "No se pudo contactar la API de tipo de cambio"},
            status=502,
        )

    rates = data.get("rates", {})
    if moneda not in rates:
        logger.warning("Moneda no soportada: %s", moneda)
        return JsonResponse(
            {"error": f"Moneda no soportada: {moneda}"},
            status=400,
        )

    tasa_moneda = rates[moneda]
    usd_por_moneda = 1 / tasa_moneda
    resultado = monto * usd_por_moneda

    logger.info("Conversión exitosa %s %s -> %s USD", monto, moneda, round(resultado, 4))
    return JsonResponse(
        {
            "monto": monto,
            "moneda": moneda,
            "resultado_usd": round(resultado, 4),
            "usd_por_moneda": usd_por_moneda,
            "fecha": data.get("date"),
            "tasa_base": "USD",
        }
    )