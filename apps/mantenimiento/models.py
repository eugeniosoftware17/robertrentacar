from decimal import Decimal

from django.db import models

from apps.vehiculos.models import Vehiculo


class Mantenimiento(models.Model):
    class Tipo(models.TextChoices):
        PREVENTIVO = 'preventivo', 'Preventivo'
        CORRECTIVO = 'correctivo', 'Correctivo'
        REVISION = 'revision', 'Revisión general'

    class Estado(models.TextChoices):
        PROGRAMADO = 'programado', 'Programado'
        EN_PROCESO = 'en_proceso', 'En proceso'
        COMPLETADO = 'completado', 'Completado'
        CANCELADO = 'cancelado', 'Cancelado'

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name='Vehículo',
    )
    fecha = models.DateField('Fecha')
    tipo = models.CharField('Tipo', max_length=20, choices=Tipo.choices, default=Tipo.REVISION)
    estado = models.CharField('Estado', max_length=20, choices=Estado.choices, default=Estado.PROGRAMADO)
    costo = models.DecimalField('Costo (RD$)', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    kilometraje = models.PositiveIntegerField('Kilometraje', blank=True, null=True)
    descripcion = models.TextField('Descripción', blank=True)
    proximo_servicio = models.DateField('Próximo servicio', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-creado_en']
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'

    def __str__(self):
        return f'{self.vehiculo.placa} — {self.get_tipo_display()} ({self.fecha})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._sincronizar_vehiculo()

    def _sincronizar_vehiculo(self):
        vehiculo = self.vehiculo
        if self.estado in (self.Estado.PROGRAMADO, self.Estado.EN_PROCESO):
            if vehiculo.estado != Vehiculo.Estado.MANTENIMIENTO:
                vehiculo.estado = Vehiculo.Estado.MANTENIMIENTO
                vehiculo.save(update_fields=['estado'])
        elif self.estado == self.Estado.COMPLETADO:
            if self.proximo_servicio:
                vehiculo.prox_mantenimiento = self.proximo_servicio
                vehiculo.save(update_fields=['prox_mantenimiento'])
            from apps.reservas.services import actualizar_estado_vehiculo
            actualizar_estado_vehiculo(vehiculo)
