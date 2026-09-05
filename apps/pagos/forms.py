from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from apps.reservas.models import Reserva

from .models import Pago


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = [
            'reserva', 'monto', 'tipo', 'metodo', 'referencia',
            'tarjeta_tipo', 'tarjeta_ultimos4', 'tarjeta_vencimiento', 'tarjeta_autorizacion',
            'notas',
        ]
        widgets = {
            'reserva': forms.Select(attrs={'class': 'mod-input', 'id': 'id_reserva_pago'}),
            'monto': forms.NumberInput(attrs={
                'class': 'mod-input',
                'step': '0.01',
                'min': '0.01',
                'id': 'id_monto_pago',
            }),
            'tipo': forms.Select(attrs={'class': 'mod-input', 'id': 'id_tipo_pago'}),
            'metodo': forms.Select(attrs={'class': 'mod-input'}),
            'referencia': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Opcional'}),
            'tarjeta_tipo': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Visa, Mastercard…'}),
            'tarjeta_ultimos4': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '••••', 'maxlength': '4'}),
            'tarjeta_vencimiento': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'MM/AA'}),
            'tarjeta_autorizacion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'No. de autorización'}),
            'notas': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reserva'].queryset = Reserva.objects.select_related(
            'cliente', 'vehiculo',
        ).exclude(estado=Reserva.Estado.CANCELADA).order_by('-fecha_inicio')
        self.fields['reserva'].label_from_instance = self._etiqueta_reserva

    @staticmethod
    def _etiqueta_reserva(reserva):
        return (
            f'#{reserva.pk} — {reserva.cliente.nombre_completo} · '
            f'{reserva.vehiculo.placa} · USD$ {reserva.precio_total:,.0f} '
            f'(saldo USD$ {reserva.saldo_pendiente:,.0f})'
        )

    def clean(self):
        cleaned = super().clean()
        reserva = cleaned.get('reserva')
        monto = cleaned.get('monto')
        tipo = cleaned.get('tipo')

        if not reserva or monto is None:
            return cleaned

        if monto <= 0:
            raise ValidationError({'monto': 'El monto debe ser mayor que cero.'})

        if tipo == Pago.Tipo.REEMBOLSO:
            if monto > reserva.total_pagado:
                raise ValidationError({
                    'monto': f'El reembolso no puede superar lo pagado (USD$ {reserva.total_pagado:,.2f}).',
                })
        elif monto > reserva.saldo_pendiente:
            raise ValidationError({
                'monto': (
                    f'El monto supera el saldo pendiente de la reserva '
                    f'(USD$ {reserva.saldo_pendiente:,.2f}). '
                    f'Total alquiler: USD$ {reserva.precio_total:,.2f} · '
                    f'Pagado: USD$ {reserva.total_pagado:,.2f}.'
                ),
            })

        return cleaned
