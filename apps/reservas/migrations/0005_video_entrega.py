from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0004_reserva_requiere_contacto_web'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reserva',
            old_name='foto_entrega',
            new_name='video_entrega',
        ),
        migrations.AlterField(
            model_name='reserva',
            name='video_entrega',
            field=models.FileField(
                blank=True,
                help_text='Registro en video del estado del vehículo al entregarlo.',
                null=True,
                upload_to='reservas/entrega/videos/',
                verbose_name='Video de entrega',
            ),
        ),
    ]
