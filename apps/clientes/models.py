from django.db import models


class Cliente(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    documento = models.CharField('Cédula / Pasaporte', max_length=20, unique=True)
    telefono = models.CharField('Teléfono', max_length=20)
    email = models.EmailField('Correo', blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    nacionalidad = models.CharField('Nacionalidad', max_length=60, blank=True)
    ocupacion = models.CharField('Ocupación', max_length=80, blank=True)
    pasaporte = models.CharField(
        'Pasaporte', max_length=30, blank=True,
        help_text='Para clientes extranjeros, si aplica.',
    )
    lugar_expedicion = models.CharField(
        'Expedido en', max_length=80, blank=True,
        help_text='Lugar de expedición de la cédula o pasaporte.',
    )
    licencia_numero = models.CharField('Número de licencia', max_length=30)
    licencia_vence = models.DateField('Vencimiento de licencia')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
