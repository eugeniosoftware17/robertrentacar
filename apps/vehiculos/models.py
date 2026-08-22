from decimal import Decimal
from types import SimpleNamespace

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class CategoriaVehiculo(models.Model):
    nombre = models.CharField('Nombre', max_length=60)
    slug = models.SlugField('Identificador', max_length=40, unique=True)
    activa = models.BooleanField('Activa', default=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría de vehículo'
        verbose_name_plural = 'Categorías de vehículo'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre) or 'categoria'
        base = self.slug
        n = 2
        while CategoriaVehiculo.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f'{base}-{n}'
            n += 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener_o_crear_default(cls):
        obj = cls.objects.filter(activa=True).order_by('orden', 'pk').first()
        if obj:
            return obj
        return cls.objects.create(nombre='General', slug='general', orden=0)

    @classmethod
    def activas(cls):
        return cls.objects.filter(activa=True).order_by('orden', 'nombre')


class Vehiculo(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        RENTADO = 'rentado', 'Rentado'
        MANTENIMIENTO = 'mantenimiento', 'En mantenimiento'

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
    categoria = models.ForeignKey(
        CategoriaVehiculo,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name='Categoría',
    )
    transmision = models.CharField(
        'Transmisión',
        max_length=20,
        choices=Transmision.choices,
        default=Transmision.AUTOMATICO,
    )
    tarifa_diaria = models.DecimalField('Tarifa diaria (RD$)', max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(
        'Precio de compra (RD$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Lo que costó adquirir el vehículo. Se usa para calcular la rentabilidad.',
    )
    fecha_compra = models.DateField('Fecha de compra', blank=True, null=True)
    descripcion_web = models.TextField('Descripción (web)', blank=True)
    descripcion_web_en = models.TextField(
        'Descripción (web, inglés)', blank=True,
        help_text='Si la dejas vacía, se usa la descripción en español para los visitantes en inglés.',
    )
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
    foto_url = models.URLField(
        'Enlace de la foto',
        max_length=500,
        blank=True,
        help_text='Alternativa a subir un archivo: pega el link de una imagen ya alojada en otro sitio.',
    )
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
        if self.foto_url:
            return [SimpleNamespace(url=self.foto_url)]
        return []

    @property
    def tiene_foto(self):
        return bool(self.foto or self.foto_url)


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
