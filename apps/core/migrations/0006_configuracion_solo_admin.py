from django.db import migrations


def quitar_configuracion_de_empleados(apps, schema_editor):
    AccesoModulo = apps.get_model('core', 'AccesoModulo')
    AccesoModulo.objects.filter(modulo='configuracion').update(permitido=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_accesomodulo_options_alter_accesomodulo_modulo'),
    ]

    operations = [
        migrations.RunPython(quitar_configuracion_de_empleados, migrations.RunPython.noop),
    ]
