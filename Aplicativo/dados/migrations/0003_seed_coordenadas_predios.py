# Migracao de dados: preenche coordenadas aproximadas dos predios

from django.db import migrations

# Coordenadas aproximadas dos predios da PUC-Rio (campus Gavea), usadas
# como ponto de partida para os marcadores no mapa interativo. Podem
# (e devem) ser ajustadas depois pelo grupo, via Django admin.
COORDENADAS_POR_SIGLA = {
    'L': ('-22.979300', '-43.232000'),
    'F': ('-22.979000', '-43.232200'),
    'K': ('-22.979500', '-43.232500'),
    'LF': ('-22.979700', '-43.231800'),
    'IAG': ('-22.978800', '-43.232800'),
    'RDC': ('-22.980000', '-43.233000'),
    'CY': ('-22.979200', '-43.233500'),
    'CI': ('-22.979800', '-43.231200'),
    'S': ('-22.978000', '-43.234000'),
    'PL': ('-22.980200', '-43.232200'),
}

def seed_coordenadas(apps, schema_editor):
    Predio = apps.get_model('dados', 'Predio')
    for sigla, (lat, lng) in COORDENADAS_POR_SIGLA.items():
        Predio.objects.filter(sigla=sigla, latitude__isnull=True).update(
            latitude=lat,
            longitude=lng,
        )


def remover_coordenadas(apps, schema_editor):
    Predio = apps.get_model('dados', 'Predio')
    Predio.objects.filter(sigla__in=COORDENADAS_POR_SIGLA.keys()).update(
        latitude=None,
        longitude=None,
    )

class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0002_predio_latitude_predio_longitude'),
    ]

    operations = [
        migrations.RunPython(seed_coordenadas, remover_coordenadas),
    ]
