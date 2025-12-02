from django.core.management.base import BaseCommand
from mercados.models import Pais


class Command(BaseCommand):
    help = "Carga o actualiza los 3 países base del proyecto NUAM en la base de datos"

    def handle(self, *args, **kwargs):
        paises = [
            {
                "codigo": "CHL",
                "nombre": "Chile",
                "moneda": "CLP",
                "bolsa_nombre": "Bolsa de Santiago",
                "ley_bursatil": "Ley 18.045",
                "texto_resumen": "Principal mercado bursátil chileno, regulado por la CMF.",
            },
            {
                "codigo": "COL",
                "nombre": "Colombia",
                "moneda": "COP",
                "bolsa_nombre": "Bolsa de Valores de Colombia",
                "ley_bursatil": "Ley 964/2005",
                "texto_resumen": "Mercado colombiano integrado en la alianza del Pacífico.",
            },
            {
                "codigo": "PER",
                "nombre": "Perú",
                "moneda": "PEN",
                "bolsa_nombre": "Bolsa de Valores de Lima",
                "ley_bursatil": "Ley 26702",
                "texto_resumen": "Mercado peruano de valores con integración regional.",
            },
        ]

        self.stdout.write(self.style.NOTICE("🌎 Cargando países NUAM..."))

        for p in paises:
            obj, created = Pais.objects.update_or_create(
                codigo=p["codigo"], defaults=p
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Creado: {p['nombre']}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚙️  Actualizado: {p['nombre']}"))

        total = Pais.objects.count()
        self.stdout.write(self.style.SUCCESS(f"✔️ Total de países en BD: {total}"))
