from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0005_home_diseno'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='logo',
            field=models.ImageField(
                blank=True,
                help_text='PNG con fondo transparente recomendado. Altura ideal: 40–56 px.',
                null=True,
                upload_to='sitio/logo/',
                verbose_name='Logo del sitio',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_nombre_junto_logo',
            field=models.BooleanField(
                default=True,
                help_text='Si desactivas, solo se verá la imagen del logo en el encabezado.',
                verbose_name='Mostrar nombre junto al logo',
            ),
        ),
    ]
