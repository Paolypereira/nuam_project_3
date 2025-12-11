from django.shortcuts import render  # si no lo usas, puedes borrarlo
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
import requests

logger = logging.getLogger(__name__)

@api_view(['GET'])
def ping(request):
    return Response({'message': 'currency-service OK'})

@api_view(['GET'])
def convertir_moneda(request):
    monto_str = request.GET.get("monto", "").strip()
    if not monto_str:
        logger.warning("Intento de conversión sin monto")
        return Response({"error": "Debe indicar un monto numérico"}, status=400)
    try:
        monto = float(monto_str)
    except ValueError:
        logger.warning("Monto inválido: %s", monto_str)
        return Response({"error": "El monto debe ser un número válido"}, status=400)

    moneda = request.GET.get("moneda", "CLP")

    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        logger.error("Fallo al llamar API de tipo de cambio", exc_info=True)
        return Response(
            {"error": "No se pudo contactar la API de tipo de cambio"},
            status=502,
        )

    rates = data.get("rates", {})
    if moneda not in rates:
        logger.warning("Moneda no soportada: %s", moneda)
        return Response(
            {"error": f"Moneda no soportada: {moneda}"},
            status=400,
        )

    tasa_moneda = rates[moneda]
    usd_por_moneda = 1 / tasa_moneda
    resultado = monto * usd_por_moneda

    logger.info("Conversión exitosa %s %s -> %s USD", monto, moneda, round(resultado, 4))

    return Response(
        {
            "monto": monto,
            "moneda": moneda,
            "resultado_usd": round(resultado, 4),
            "usd_por_moneda": usd_por_moneda,
            "fecha": data.get("date"),
            "tasa_base": "USD",
        }
    )
