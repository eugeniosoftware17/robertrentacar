from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0012_pie_copyright'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuracionsitio',
            name='pie_copyright_texto',
        ),
        migrations.RemoveField(
            model_name='configuracionsitio',
            name='pie_copyright_url',
        ),
        migrations.AlterField(
            model_name='configuracionsitio',
            name='mostrar_pie_copyright',
            field=models.BooleanField(
                default=True,
                help_text='Muestra el enlace a Cloud Tech System en el pie del sitio público.',
                verbose_name='Mostrar crédito del desarrollador',
            ),
        ),
    ]
