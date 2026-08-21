from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ConfiguracionEmpresa(models.Model):
    nombre = models.CharField('Nombre comercial', max_length=120, default='Deja Vu Rent Car')
    telefono = models.CharField('Teléfono', max_length=30, blank=True)
    email = models.EmailField('Correo', blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    ciudad = models.CharField(
        'Ciudad',
        max_length=80,
        default='Santiago',
        help_text='Se usa en el SEO del sitio para posicionar en búsquedas de esta ciudad.',
    )
    rnc = models.CharField('RNC', max_length=20, blank=True)
    notas_contrato = models.TextField('Cláusulas del contrato', blank=True)
    bloqueo_inactividad_horas = models.PositiveSmallIntegerField(
        'Bloqueo por inactividad (horas)',
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(168)],
        help_text='Cierra la sesión del panel si no hay actividad durante este tiempo (1 a 168 horas).',
    )

    class Meta:
        verbose_name = 'Configuración de empresa'
        verbose_name_plural = 'Configuración de empresa'

    def __str__(self):
        return self.nombre

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
