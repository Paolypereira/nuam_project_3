from rest_framework import serializers
from .models import Pais, Normativa, Empresa

# ---------------------------------------------------------------------
# Serializers existentes
# ---------------------------------------------------------------------
class NormativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Normativa
        fields = '__all__'


class PaisSerializer(serializers.ModelSerializer):
    normas = NormativaSerializer(many=True, read_only=True)

    class Meta:
        model = Pais
        fields = [
            'codigo', 'nombre', 'moneda',
            'bolsa_nombre', 'ley_bursatil',
            'texto_resumen', 'normas'
        ]


# ---------------------------------------------------------------------
# Nuevo serializer para el mantenedor de Empresas
# ---------------------------------------------------------------------
class EmpresaSerializer(serializers.ModelSerializer):
    # Campo adicional solo lectura: muestra el código del país
    pais_codigo = serializers.CharField(source='pais.codigo', read_only=True)
    pais_nombre = serializers.CharField(source='pais.nombre', read_only=True)

    class Meta:
        model = Empresa
        fields = [
            'ticker', 'nombre', 'pais', 'pais_codigo', 'pais_nombre',
            'sector', 'moneda', 'capitalizacion',
            'mercado', 'fuente', 'fecha_reporte'
        ]
