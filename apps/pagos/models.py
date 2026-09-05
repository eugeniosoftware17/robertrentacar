from decimal import Decimal

from django.db import models

from apps.reservas.models import Reserva


class Pago(models.Model):
    class Tipo(models.TextChoices):
        DEPOSITO = 'deposito', 'Depósito'
        PARCIAL = 'parcial', 'Pago parcial'
        TOTAL = 'total', 'Pago total'
        REEMBOLSO = 'reembolso', 'Reembolso'

    class Metodo(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo (USD$)'
        DOLAR = 'dolar', 'Dólar (US$)'
        EURO = 'euro', 'Euro (€)'
        TARJETA = 'tarjeta', 'Tarjeta'
        TRANSFERENCIA = 'transferencia', 'Transferencia'

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.PROTECT,
        related_name='pagos',
        verbose_name='Reserva',
    )
    monto = models.DecimalField('Monto (USD$)', max_digits=10, decimal_places=2)
    tipo = models.CharField('Tipo', max_length=20, choices=Tipo.choices, default=Tipo.PARCIAL)
    metodo = models.CharField('Método', max_length=20, choices=Metodo.choices, default=Metodo.EFECTIVO)
    referencia = models.CharField('Referencia', max_length=60, blank=True)
    tarjeta_tipo = models.CharField('Tipo de tarjeta', max_length=30, blank=True)
    tarjeta_ultimos4 = models.CharField('Últimos 4 dígitos', max_length=4, blank=True)
    tarjeta_vencimiento = models.CharField(
        'Vencimiento de tarjeta', max_length=10, blank=True,
        help_text='MM/AA',
    )
    tarjeta_autorizacion = models.CharField('No. de autorización', max_length=40, blank=True)
    notas = models.TextField('Notas', blank=True)
    fecha = models.DateTimeField('Fecha del pago', auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'USD$ {self.monto} — Reserva #{self.reserva_id}'
