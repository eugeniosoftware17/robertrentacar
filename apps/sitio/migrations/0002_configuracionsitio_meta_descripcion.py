from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsitio',
            name='meta_descripcion',
            field=models.CharField(
                blank=True,
                help_text='Texto para Google (máx. 160 caracteres). Si está vacío se genera automáticamente.',
                max_length=160,
                verbose_name='Meta descripción (SEO inicio)',
            ),
        ),
    ]
