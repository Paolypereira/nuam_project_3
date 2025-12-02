# mercados/models.py
from django.db import models
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json


class Pais(models.Model):
    codigo = models.CharField(max_length=3, primary_key=True)          # CHL, COL, PER
    nombre = models.CharField(max_length=50)
    moneda = models.CharField(max_length=3)                            # CLP, COP, PEN
    bolsa_nombre = models.CharField(max_length=100)
    ley_bursatil = models.CharField(max_length=200)
    texto_resumen = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "paises"

    def __str__(self):
        return self.nombre


class Normativa(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="normas")
    titulo = models.CharField(max_length=200)
    numero = models.CharField(max_length=50, blank=True)
    fecha_promulgacion = models.DateField()
    url_oficial = models.URLField(blank=True)
    tema = models.CharField(max_length=50)  # ej: tributario, listado, inversión extranjera

    def __str__(self):
        return f"{self.titulo} ({self.pais.codigo})"


class ValorInstrumento(models.Model):
    instrumento = models.ForeignKey("InstrumentoNoInscrito", on_delete=models.CASCADE)
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=20, decimal_places=2)
    moneda = models.CharField(max_length=3, default="CLP")  # CLP, COP, PEN


class InstrumentoNoInscrito(models.Model):
    """
    Instrumentos que aún no han sido inscritos en ninguna de las bolsas NUAM
    pero deben ser monitoreados por compliance.
    """
    nombre = models.CharField(max_length=255)
    emisor = models.CharField(max_length=255)
    pais_origen = models.ForeignKey(Pais, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)          # acción, bono, ETF, etc.
    fecha_solicitud = models.DateField()
    estado = models.CharField(max_length=50, default="En revisión")

    def __str__(self):
        return f"{self.nombre} - {self.emisor} ({self.pais_origen.codigo})"


class CalificacionTributaria(models.Model):
    """
    Guarda las calificaciones tributarias que debe cumplir cada emisor
    según la legislación local.
    """
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    tasa_retencion = models.DecimalField(max_digits=5, decimal_places=2)
    vigente_desde = models.DateField()
    comentarios = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "calificaciones tributarias"

    def __str__(self):
        return f"{self.pais.nombre} - {self.descripcion}"


class HistorialCambio(models.Model):
    """
    Bitácora de cambios normativos o de tasas que afecten a los instrumentos.
    """
    TIPOS_CAMBIO = [
        ("NORMATIVA", "Normativa"),
        ("TASA", "Tasa tributaria"),
        ("LISTADO", "Requisito de listado"),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CAMBIO)
    pais_afectado = models.ForeignKey(Pais, on_delete=models.CASCADE)
    descripcion = models.TextField()
    usuario = models.CharField(max_length=150, blank=True)  # si usas auth.User cámbialo

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.pais_afectado.codigo} ({self.fecha:%Y-%m-%d %H:%M})"


class ArchivoCargaMasiva(models.Model):
    """
    Almacena archivos CSV/Excel para cargas masivas de instrumentos o precios.
    """
    archivo = models.FileField(upload_to="cargas/%Y/%m/")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)
    resultado = models.TextField(blank=True)

    def __str__(self):
        return f"{self.archivo.name} - {'OK' if self.procesado else 'Pendiente'}"


# ------------------------------
# Modelo: Empresa
# ------------------------------
class Empresa(models.Model):
    """
    Empresa / Emisor listado o monitoreado, basado en la hoja 'Nemo - Market Cap' del Excel de Nuam.
    """
    ticker = models.CharField(max_length=20, unique=True)  # Nemotécnico / Ticker
    nombre = models.CharField(max_length=255)

    # Relación con país (usa tu modelo Pais con PK=codigo).
    pais = models.ForeignKey(
        Pais,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empresas",
    )

    sector = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=10, blank=True, null=True)

    # Market Cap / Capitalización bursátil
    capitalizacion = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
    )

    # Metadatos útiles
    mercado = models.CharField(max_length=100, blank=True, null=True)
    fuente = models.CharField(max_length=100, blank=True, null=True)
    fecha_reporte = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["ticker"]

    def __str__(self):
        return f"{self.ticker} - {self.nombre}"


def empresa_a_dict(empresa):
    """Convierte una instancia de Empresa a un dict serializable JSON."""
    data = model_to_dict(empresa)
    # Si hay campos que no quieras enviar al topic, elimínalos aquí:
    # data.pop("campo_x", None)
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))
