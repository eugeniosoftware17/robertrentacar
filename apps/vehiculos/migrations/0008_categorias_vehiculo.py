import django.db.models.deletion
from django.db import migrations, models


CATEGORIAS_INICIALES = (
    ('sedan', 'Sedán', 1),
    ('suv', 'SUV', 2),
    ('pickup', 'Pick-up', 3),
    ('van', 'Van', 4),
    ('lujo', 'Lujo', 5),
)


def sembrar_categorias(apps, schema_editor):
    CategoriaVehiculo = apps.get_model('vehiculos', 'CategoriaVehiculo')
    for slug, nombre, orden in CATEGORIAS_INICIALES:
        CategoriaVehiculo.objects.get_or_create(
            slug=slug,
            defaults={'nombre': nombre, 'orden': orden, 'activa': True},
        )


def asignar_categorias_a_vehiculos(apps, schema_editor):
    Vehiculo = apps.get_model('vehiculos', 'Vehiculo')
    CategoriaVehiculo = apps.get_model('vehiculos', 'CategoriaVehiculo')
    default = CategoriaVehiculo.objects.order_by('orden', 'pk').first()
    for vehiculo in Vehiculo.objects.all():
        categoria = CategoriaVehiculo.objects.filter(slug=vehiculo.categoria_legacy).first() or default
        vehiculo.categoria = categoria
        vehiculo.save(update_fields=['categoria'])


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculos', '0007_vehiculo_descripcion_web_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, verbose_name='Nombre')),
                ('slug', models.SlugField(max_length=40, unique=True, verbose_name='Identificador')),
                ('activa', models.BooleanField(default=True, verbose_name='Activa')),
                ('orden', models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
            ],
            options={
                'verbose_name': 'Categoría de vehículo',
                'verbose_name_plural': 'Categorías de vehículo',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.RunPython(sembrar_categorias, migrations.RunPython.noop),
        migrations.RenameField(
            model_name='vehiculo',
            old_name='categoria',
            new_name='categoria_legacy',
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='categoria',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='vehiculos',
                to='vehiculos.categoriavehiculo',
                verbose_name='Categoría',
            ),
        ),
        migrations.RunPython(asignar_categorias_a_vehiculos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='vehiculo',
            name='categoria_legacy',
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='categoria',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='vehiculos',
                to='vehiculos.categoriavehiculo',
                verbose_name='Categoría',
            ),
        ),
    ]
