from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0004_codigo_personalizado'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_diseno',
            field=models.CharField(
                choices=[
                    ('clasico', 'Clásico — texto + panel lateral'),
                    ('foto', 'Foto de fondo — hero amplio con imagen'),
                    ('centrado', 'Centrado — texto al medio'),
                    ('compacto', 'Compacto — hero más pequeño'),
                    ('split', 'Dividido — imagen a un lado'),
                ],
                default='clasico',
                max_length=20,
                verbose_name='Diseño del inicio',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_fondo_imagen',
            field=models.ImageField(
                blank=True,
                help_text='Recomendado: 1920×900 px o similar. JPG o WebP.',
                null=True,
                upload_to='sitio/home/',
                verbose_name='Imagen de fondo del inicio',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_fondo_opacidad',
            field=models.PositiveSmallIntegerField(
                default=60,
                help_text='0 = sin oscurecer, 100 = muy oscuro. Mejora la lectura del texto.',
                verbose_name='Oscurecer foto (%)',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_categorias',
            field=models.BooleanField(default=True, verbose_name='Sección categorías'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_contador',
            field=models.BooleanField(default=True, verbose_name='Contador de vehículos'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_cta',
            field=models.BooleanField(default=True, verbose_name='Llamada a la acción final'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_destacados',
            field=models.BooleanField(default=True, verbose_name='Vehículos destacados'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_panel',
            field=models.BooleanField(default=True, verbose_name='Panel «¿Por qué reservar?»'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='home_mostrar_redes_hero',
            field=models.BooleanField(default=True, verbose_name='Redes sociales en el hero'),
        ),
    ]
