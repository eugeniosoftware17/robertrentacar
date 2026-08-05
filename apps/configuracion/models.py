from django.db import models


class ConfiguracionEmpresa(models.Model):
    nombre = models.CharField('Nombre comercial', max_length=120, default='Deja Vu Rent Car')
    telefono = models.CharField('Teléfono', max_length=30, blank=True)
    email = models.EmailField('Correo', blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    rnc = models.CharField('RNC', max_length=20, blank=True)
    notas_contrato = models.TextField('Cláusulas del contrato', blank=True)

    class Meta:
        verbose_name = 'Configuración de empresa'
        verbose_name_plural = 'Configuración de empresa'

    def __str__(self):
        return self.nombre

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
