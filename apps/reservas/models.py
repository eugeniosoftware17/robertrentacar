from datetime import time, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo


class Reserva(models.Model):
    class Origen(models.TextChoices):
        PANEL = 'panel', 'Panel'
        WEB = 'web', 'Sitio web'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADA = 'confirmada', 'Confirmada'
        ACTIVA = 'activa', 'Activa'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Cliente',
    )
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Vehículo',
    )
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    hora_entrega = models.TimeField('Hora de entrega', default=time(9, 0))
    hora_devolucion = models.TimeField('Hora de devolución', default=time(17, 0))
    lugar_entrega = models.CharField('Lugar de entrega', max_length=120, default='Sucursal')
    lugar_devolucion = models.CharField('Lugar de devolución', max_length=120, default='Sucursal')
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    precio_total = models.DecimalField(
        'Precio total (RD$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    deposito = models.DecimalField(
        'Depósito inicial (RD$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Se registra automáticamente como pago al guardar la reserva.',
    )
    notas = models.TextField('Notas', blank=True)
    origen = models.CharField(
        'Origen',
        max_length=10,
        choices=Origen.choices,
        default=Origen.PANEL,
    )
    requiere_contacto_web = models.BooleanField(
        'Pendiente de contacto (web)',
        default=False,
        help_text='Alerta en el panel hasta marcar como contactado.',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Combustible(models.TextChoices):
        VACIO = 'vacio', 'Vacío'
        CUARTO = 'cuarto', '1/4'
        MEDIO = 'medio', '1/2'
        TRES_CUARTOS = 'tres_cuartos', '3/4'
        LLENO = 'lleno', 'Lleno'

    km_entrega = models.PositiveIntegerField('Km al entregar', blank=True, null=True)
    km_devolucion = models.PositiveIntegerField('Km al devolver', blank=True, null=True)
    combustible_entrega = models.CharField(
        'Combustible al entregar',
        max_length=20,
        choices=Combustible.choices,
        blank=True,
    )
    combustible_devolucion = models.CharField(
        'Combustible al devolver',
        max_length=20,
        choices=Combustible.choices,
        blank=True,
    )
    notas_entrega = models.TextField('Observaciones de entrega', blank=True)
    notas_devolucion = models.TextField('Observaciones de devolución', blank=True)
    danos_entrega = models.TextField('Daños preexistentes', blank=True)
    danos_devolucion = models.TextField('Daños al devolver', blank=True)
    foto_entrega = models.ImageField('Foto entrega', upload_to='reservas/entrega/', blank=True, null=True)
    foto_devolucion = models.ImageField('Foto devolución', upload_to='reservas/devolucion/', blank=True, null=True)
    entrega_registrada = models.BooleanField('Entrega registrada', default=False)
    devolucion_registrada = models.BooleanField('Devolución registrada', default=False)

    class Meta:
        ordering = ['-fecha_inicio', '-creado_en']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'Reserva #{self.pk} — {self.cliente} / {self.vehiculo.placa}'

    @property
    def dias(self):
        if self.fecha_fin and self.fecha_inicio:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0

    def calcular_precio(self):
        if self.fecha_inicio and self.fecha_fin and self.vehiculo_id:
            dias = max(self.dias, 1)
            return self.vehiculo.tarifa_diaria * dias
        return Decimal('0.00')

    def clean(self):
        super().clean()

        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de fin no puede ser anterior al inicio.'})

        if self.estado == self.Estado.CANCELADA:
            return

        if self.cliente_id and self.cliente.licencia_vence < timezone.localdate():
            raise ValidationError({'cliente': 'La licencia del cliente está vencida.'})

        if not self.vehiculo_id or not self.fecha_inicio or not self.fecha_fin:
            return

        if self.vehiculo.estado == Vehiculo.Estado.MANTENIMIENTO:
            raise ValidationError({'vehiculo': 'El vehículo está en mantenimiento.'})

        if self.vehiculo.seguro_vence and self.vehiculo.seguro_vence < self.fecha_inicio:
            raise ValidationError({'vehiculo': 'El seguro del vehículo está vencido para esa fecha.'})

        conflicto = Reserva.objects.filter(
            vehiculo=self.vehiculo,
            fecha_inicio__lte=self.fecha_fin,
            fecha_fin__gte=self.fecha_inicio,
        ).exclude(estado=self.Estado.CANCELADA)

        if self.pk:
            conflicto = conflicto.exclude(pk=self.pk)

        if conflicto.exists():
            raise ValidationError(
                'El vehículo ya tiene una reserva en conflicto para esas fechas.'
            )

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_fin and self.vehiculo_id:
            self.precio_total = self.calcular_precio()
        super().save(*args, **kwargs)
        self._sincronizar_deposito_pago()
        from .services import actualizar_estado_vehiculo
        actualizar_estado_vehiculo(self.vehiculo)

    def _sincronizar_deposito_pago(self):
        from apps.pagos.models import Pago

        marcador = 'Depósito inicial (automático)'
        pago_auto = self.pagos.filter(notas=marcador, tipo=Pago.Tipo.DEPOSITO).first()

        if self.deposito <= 0:
            if pago_auto:
                pago_auto.delete()
            return

        if pago_auto:
            if pago_auto.monto != self.deposito:
                pago_auto.monto = self.deposito
                pago_auto.save(update_fields=['monto'])
        else:
            Pago.objects.create(
                reserva=self,
                monto=self.deposito,
                tipo=Pago.Tipo.DEPOSITO,
                metodo=Pago.Metodo.EFECTIVO,
                notas=marcador,
            )

    @property
    def total_pagado(self):
        from apps.pagos.models import Pago

        cobros = self.pagos.exclude(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t']
        reembolsos = self.pagos.filter(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t']
        cobros = cobros or Decimal('0.00')
        reembolsos = reembolsos or Decimal('0.00')
        return max(cobros - reembolsos, Decimal('0.00'))

    @property
    def saldo_pendiente(self):
        return max(self.precio_total - self.total_pagado, Decimal('0.00'))

    @property
    def estado_pago(self):
        if self.precio_total <= 0:
            return 'pendiente'
        if self.saldo_pendiente <= 0:
            return 'pagado'
        if self.total_pagado > 0:
            return 'parcial'
        return 'pendiente'

    @property
    def estado_pago_label(self):
        labels = {
            'pagado': 'Pagado',
            'parcial': 'Pago parcial',
            'pendiente': 'Sin pagar',
        }
        return labels[self.estado_pago]

    @property
    def es_entrega_hoy(self):
        return self.fecha_inicio == timezone.localdate()

    @property
    def es_devolucion_hoy(self):
        return self.fecha_fin == timezone.localdate()

    @property
    def puede_registrar_entrega(self):
        if self.estado in (Reserva.Estado.CANCELADA, Reserva.Estado.COMPLETADA):
            return False
        return self.fecha_inicio <= timezone.localdate()

    @property
    def puede_registrar_devolucion(self):
        if self.estado == Reserva.Estado.CANCELADA:
            return False
        if self.devolucion_registrada:
            return False
        return self.estado == Reserva.Estado.ACTIVA or self.fecha_fin <= timezone.localdate()

    @property
    def tipo_movimiento(self):
        hoy = timezone.localdate()
        manana = hoy + timedelta(days=1)

        if self.fecha_inicio in (hoy, manana):
            return 'Entrega'
        if self.fecha_fin in (hoy, manana):
            return 'Devolución'
        return 'Reserva'
