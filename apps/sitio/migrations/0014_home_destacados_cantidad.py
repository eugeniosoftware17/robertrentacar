from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0013_creador_cloud_tech_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_destacados_cantidad',
            field=models.PositiveSmallIntegerField(
                default=6,
                help_text='Cuántos vehículos mostrar en la sección destacados del home (1–24).',
                verbose_name='Cantidad en inicio',
            ),
        ),
    ]
