from django.db import migrations


def cargar_datos_reales(apps, schema_editor):
    ConfiguracionEmpresa = apps.get_model('configuracion', 'ConfiguracionEmpresa')
    ConfiguracionEmpresa.objects.update_or_create(
        pk=1,
        defaults={
            'nombre': 'Robert Rent A Car',
            'telefono': '+1 809-399-9540',
            'direccion': 'Av. Hispanoamericana, cerca de UAPA, Santiago de los Caballeros',
            'ciudad': 'Santiago de los Caballeros',
        },
    )


def revertir(apps, schema_editor):
    # No se revierte: son datos reales del negocio, no hay un valor
    # anterior significativo al que volver.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0002_configuracionempresa_ciudad'),
    ]

    operations = [
        migrations.RunPython(cargar_datos_reales, revertir),
    ]
