from django.db import migrations, models


def poblar_slugs(apps, schema_editor):
    Vehiculo = apps.get_model('vehiculos', 'Vehiculo')
    from django.utils.text import slugify

    for vehiculo in Vehiculo.objects.all().order_by('pk'):
        base = slugify(f'{vehiculo.marca}-{vehiculo.modelo}-{vehiculo.anio}') or 'vehiculo'
        candidato = base
        n = 2
        while Vehiculo.objects.filter(slug=candidato).exclude(pk=vehiculo.pk).exists():
            candidato = f'{base}-{n}'
            n += 1
        vehiculo.slug = candidato
        vehiculo.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculos', '0003_vehiculofoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='slug',
            field=models.SlugField(
                blank=True,
                help_text='Enlace público, ej. toyota-corolla-2022',
                max_length=120,
                null=True,
                unique=True,
                verbose_name='URL web',
            ),
        ),
        migrations.RunPython(poblar_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='vehiculo',
            name='slug',
            field=models.SlugField(
                blank=True,
                help_text='Enlace público, ej. toyota-corolla-2022',
                max_length=120,
                unique=True,
                verbose_name='URL web',
            ),
        ),
    ]
