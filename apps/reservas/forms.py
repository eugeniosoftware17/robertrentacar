from django import forms
from django.core.exceptions import ValidationError

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo

from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'cliente',
            'vehiculo',
            'fecha_inicio',
            'fecha_fin',
            'hora_entrega',
            'hora_devolucion',
            'lugar_entrega',
            'lugar_devolucion',
            'estado',
            'deposito',
            'notas',
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'mod-input'}),
            'vehiculo': forms.Select(attrs={'class': 'mod-input'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'hora_entrega': forms.TimeInput(attrs={'class': 'mod-input', 'type': 'time'}),
            'hora_devolucion': forms.TimeInput(attrs={'class': 'mod-input', 'type': 'time'}),
            'lugar_entrega': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Sucursal'}),
            'lugar_devolucion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Sucursal'}),
            'estado': forms.Select(attrs={'class': 'mod-input'}),
            'deposito': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'notas': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)

    def clean(self):
        cleaned = super().clean()
        deposito = cleaned.get('deposito')
        vehiculo = cleaned.get('vehiculo')
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_fin = cleaned.get('fecha_fin')

        if deposito is not None and deposito < 0:
            raise ValidationError({'deposito': 'El depósito no puede ser negativo.'})

        if deposito and vehiculo and fecha_inicio and fecha_fin:
            dias = max((fecha_fin - fecha_inicio).days + 1, 1)
            total = vehiculo.tarifa_diaria * dias
            if deposito > total:
                raise ValidationError({
                    'deposito': (
                        f'El depósito (RD$ {deposito:,.2f}) no puede superar '
                        f'el total del alquiler (RD$ {total:,.2f}).'
                    ),
                })

        return cleaned


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'km_entrega',
            'combustible_entrega',
            'danos_entrega',
            'notas_entrega',
            'foto_entrega',
        ]
        widgets = {
            'km_entrega': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'combustible_entrega': forms.Select(attrs={'class': 'mod-input'}),
            'danos_entrega': forms.Textarea(attrs={
                'class': 'mod-input mod-textarea',
                'rows': 3,
                'placeholder': 'Rayones, abolladuras u otros daños previos…',
            }),
            'notas_entrega': forms.Textarea(attrs={
                'class': 'mod-input mod-textarea',
                'rows': 2,
                'placeholder': 'Observaciones generales…',
            }),
            'foto_entrega': forms.FileInput(attrs={'class': 'mod-input', 'accept': 'image/*'}),
        }

    def clean_km_entrega(self):
        km = self.cleaned_data.get('km_entrega')
        if km is None:
            raise ValidationError('Indica el kilometraje al entregar el vehículo.')
        vehiculo = self.instance.vehiculo
        if km < vehiculo.kilometraje:
            raise ValidationError(
                f'El km ({km:,}) no puede ser menor al registrado en flota ({vehiculo.kilometraje:,}).'
            )
        return km


class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'km_devolucion',
            'combustible_devolucion',
            'danos_devolucion',
            'notas_devolucion',
            'foto_devolucion',
        ]
        widgets = {
            'km_devolucion': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'combustible_devolucion': forms.Select(attrs={'class': 'mod-input'}),
            'danos_devolucion': forms.Textarea(attrs={
                'class': 'mod-input mod-textarea',
                'rows': 3,
                'placeholder': 'Daños nuevos detectados al devolver…',
            }),
            'notas_devolucion': forms.Textarea(attrs={
                'class': 'mod-input mod-textarea',
                'rows': 2,
                'placeholder': 'Observaciones de la devolución…',
            }),
            'foto_devolucion': forms.FileInput(attrs={'class': 'mod-input', 'accept': 'image/*'}),
        }

    def clean_km_devolucion(self):
        km = self.cleaned_data.get('km_devolucion')
        if km is None:
            raise ValidationError('Indica el kilometraje al devolver el vehículo.')
        km_entrega = self.instance.km_entrega
        if km_entrega and km < km_entrega:
            raise ValidationError(
                f'El km de devolución ({km:,}) no puede ser menor al de entrega ({km_entrega:,}).'
            )
        return km
