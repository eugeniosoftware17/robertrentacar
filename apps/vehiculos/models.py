from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Vehiculo(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        RENTADO = 'rentado', 'Rentado'
        MANTENIMIENTO = 'mantenimiento', 'En mantenimiento'

    class Categoria(models.TextChoices):
        SEDAN = 'sedan', 'Sedán'
        SUV = 'suv', 'SUV'
        PICKUP = 'pickup', 'Pick-up'
        VAN = 'van', 'Van'
        LUJO = 'lujo', 'Lujo'

    class Transmision(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        AUTOMATICO = 'automatico', 'Automático'
        CVT = 'cvt', 'CVT'

    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    anio = models.PositiveIntegerField('Año')
    placa = models.CharField('Placa', max_length=15, unique=True)
    slug = models.SlugField(
        'URL web',
        max_length=120,
        unique=True,
        blank=True,
        help_text='Enlace público, ej. toyota-corolla-2022',
    )
    categoria = models.CharField(
        'Categoría',
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.SEDAN,
    )
    transmision = models.CharField(
        'Transmisión',
        max_length=20,
        choices=Transmision.choices,
        default=Transmision.AUTOMATICO,
    )
    tarifa_diaria = models.DecimalField('Tarifa diaria (RD$)', max_digits=10, decimal_places=2)
    descripcion_web = models.TextField('Descripción (web)', blank=True)
    visible_en_web = models.BooleanField('Visible en sitio web', default=False)
    destacado_web = models.BooleanField('Destacado en inicio', default=False)
    orden_web = models.PositiveSmallIntegerField('Orden en web', default=0)
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    color = models.CharField('Color', max_length=30, blank=True)
    kilometraje = models.PositiveIntegerField('Kilometraje', default=0)
    foto = models.ImageField('Foto', upload_to='vehiculos/', blank=True, null=True)
    seguro_vence = models.DateField('Vencimiento del seguro', blank=True, null=True)
    prox_mantenimiento = models.DateField('Próximo mantenimiento', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['marca', 'modelo']
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f'{self.marca} {self.modelo} {self.anio} ({self.placa})'

    @property
    def nombre_corto(self):
        return f'{self.marca} {self.modelo} {self.anio}'

    def slug_base(self):
        return slugify(f'{self.marca}-{self.modelo}-{self.anio}') or 'vehiculo'

    def generar_slug_unico(self):
        base = self.slug_base()
        candidato = base
        n = 2
        while Vehiculo.objects.filter(slug=candidato).exclude(pk=self.pk).exists():
            candidato = f'{base}-{n}'
            n += 1
        return candidato

    def get_absolute_url(self):
        return reverse('sitio:vehiculo', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generar_slug_unico()
        super().save(*args, **kwargs)

    def fotos_para_web(self):
        """Hasta 3 imágenes para el sitio público."""
        galeria = [f.imagen for f in self.fotos_galeria.all() if f.imagen][:3]
        if galeria:
            return galeria
        if self.foto:
            return [self.foto]
        return []


class VehiculoFoto(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='fotos_galeria',
        verbose_name='Vehículo',
    )
    imagen = models.ImageField('Imagen', upload_to='vehiculos/galeria/')
    orden = models.PositiveSmallIntegerField('Orden', default=1)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Foto de vehículo'
        verbose_name_plural = 'Fotos de vehículo'
        constraints = [
            models.UniqueConstraint(fields=['vehiculo', 'orden'], name='vehiculo_foto_orden_unico'),
            models.CheckConstraint(condition=models.Q(orden__gte=1, orden__lte=3), name='vehiculo_foto_orden_1_3'),
        ]

    def __str__(self):
        return f'{self.vehiculo.placa} — foto {self.orden}'
