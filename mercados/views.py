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

# -------- CATÁLOGO EMPRESAS (frontend que lista empresas) --------
def demo_empresas(request):
    return render(request, "empresas.html", {
        "title": "Catálogo de Empresas"
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
    monto = float(request.GET.get("monto", 0))
    moneda = request.GET.get("moneda", "CLP")  # CLP, PEN, COP, etc.

    url = "https://api.exchangerate-api.com/v4/latest/USD"
    r = requests.get(url, timeout=5)
    data = r.json()

    rates = data.get("rates", {})
    if moneda not in rates:
        return JsonResponse({"error": "Moneda no soportada"}, status=400)

    tasa_moneda = rates[moneda]
    usd_por_moneda = 1 / tasa_moneda
    resultado = monto * usd_por_moneda

    return JsonResponse({
        "monto": monto,
        "moneda": moneda,
        "resultado_usd": round(resultado, 4),
        "usd_por_moneda": usd_por_moneda,
        "fecha": data.get("date"),
        "tasa_base": "USD",
    })


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
