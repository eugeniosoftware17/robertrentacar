from django.db import models


class Cliente(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    documento = models.CharField('Cédula / Pasaporte', max_length=20, unique=True)
    telefono = models.CharField('Teléfono', max_length=20)
    email = models.EmailField('Correo', blank=True)
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
