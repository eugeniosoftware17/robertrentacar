from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0003_redes_sociales'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='css_global',
            field=models.TextField(
                blank=True,
                help_text='Estilos aplicados a todas las páginas públicas. Solo administradores.',
                verbose_name='CSS global del sitio',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_html_extra',
            field=models.TextField(
                blank=True,
                help_text='Bloque HTML personalizado en la página de inicio (antes del pie de llamada a la acción).',
                verbose_name='HTML extra del inicio',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='js_global',
            field=models.TextField(
                blank=True,
                help_text='Scripts en todas las páginas (Analytics, Pixel, etc.). Solo administradores.',
                verbose_name='JavaScript global del sitio',
            ),
        ),
        migrations.AddField(
            model_name='paginainformativa',
            name='css_extra',
            field=models.TextField(
                blank=True,
                help_text='Estilos solo para esta página.',
                verbose_name='CSS de la página',
            ),
        ),
        migrations.AddField(
            model_name='paginainformativa',
            name='js_extra',
            field=models.TextField(
                blank=True,
                help_text='Scripts solo para esta página.',
                verbose_name='JavaScript de la página',
            ),
        ),
        migrations.AlterField(
            model_name='paginainformativa',
            name='contenido',
            field=models.TextField(
                help_text='Puedes usar HTML: <h2>, <p>, <img>, <iframe>, listas, etc.',
                verbose_name='Contenido (HTML)',
            ),
        ),
    ]
