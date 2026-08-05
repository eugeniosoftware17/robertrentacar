from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0002_configuracionsitio_meta_descripcion'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_facebook',
            field=models.BooleanField(default=True, verbose_name='Mostrar Facebook'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_instagram',
            field=models.BooleanField(default=True, verbose_name='Mostrar Instagram'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_tiktok',
            field=models.BooleanField(default=False, verbose_name='Mostrar TikTok'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_twitter',
            field=models.BooleanField(default=False, verbose_name='Mostrar X (Twitter)'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_whatsapp',
            field=models.BooleanField(default=True, verbose_name='Mostrar WhatsApp'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='mostrar_youtube',
            field=models.BooleanField(default=False, verbose_name='Mostrar YouTube'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='tiktok',
            field=models.URLField(blank=True, verbose_name='TikTok'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='twitter',
            field=models.URLField(blank=True, verbose_name='X (Twitter)'),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='whatsapp_flotante',
            field=models.BooleanField(
                default=True,
                help_text='Botón verde fijo en la esquina de todas las páginas.',
                verbose_name='Botón flotante de WhatsApp',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='whatsapp_mensaje',
            field=models.CharField(
                blank=True,
                default='Hola, me interesa alquilar un vehículo. ¿Tienen disponibilidad?',
                help_text='Texto prellenado cuando el cliente abre WhatsApp desde la web.',
                max_length=300,
                verbose_name='Mensaje automático de WhatsApp',
            ),
        ),
        migrations.AddField(
            model_name='configuracionsitio',
            name='youtube',
            field=models.URLField(blank=True, verbose_name='YouTube'),
        ),
        migrations.AlterField(
            model_name='configuracionsitio',
            name='whatsapp',
            field=models.CharField(
                blank=True,
                help_text='Con código de país, ej. +1 809 555 1234',
                max_length=30,
                verbose_name='WhatsApp (número)',
            ),
        ),
    ]
