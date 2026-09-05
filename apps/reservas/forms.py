import os

from django import forms
from django.core.exceptions import ValidationError

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo

from .models import ConductorAdicional, Reserva

VIDEO_ENTREGA_EXTENSIONES = {'.mp4', '.webm', '.mov', '.m4v'}
VIDEO_ENTREGA_MIMES = {
    'video/mp4',
    'video/webm',
    'video/quicktime',
    'video/x-m4v',
}
VIDEO_ENTREGA_MAX_BYTES = 100 * 1024 * 1024  # 100 MB


def validar_video_entrega(archivo):
    if not archivo:
        return

    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in VIDEO_ENTREGA_EXTENSIONES:
        raise ValidationError(
            'Formato no permitido. Usa MP4, WebM o MOV.'
        )

    content_type = getattr(archivo, 'content_type', '') or ''
    if content_type and content_type not in VIDEO_ENTREGA_MIMES:
        raise ValidationError(
            'El archivo debe ser un video (MP4, WebM o MOV).'
        )

    if archivo.size > VIDEO_ENTREGA_MAX_BYTES:
        raise ValidationError('El video no puede superar 100 MB.')


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
            'deducible',
            'posible_retorno',
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
            'deducible': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'posible_retorno': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
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
                        f'El depósito (USD$ {deposito:,.2f}) no puede superar '
                        f'el total del alquiler (USD$ {total:,.2f}).'
                    ),
                })

        return cleaned


class ConductorAdicionalForm(forms.ModelForm):
    class Meta:
        model = ConductorAdicional
        exclude = ['reserva']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Apellido'}),
            'documento': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Cédula'}),
            'pasaporte': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Opcional, para extranjeros'}),
            'direccion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '809-000-0000'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Nacionalidad'}),
            'ocupacion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Ocupación'}),
            'lugar_expedicion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Lugar de expedición'}),
            'licencia_numero': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Número de licencia'}),
            'licencia_vence': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
        }


class EntregaForm(forms.ModelForm):
    checklist_entrega = forms.MultipleChoiceField(
        label='Checklist de entrega',
        choices=Reserva.CHECKLIST_ITEMS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Reserva
        fields = [
            'km_entrega',
            'combustible_entrega',
            'danos_entrega',
            'notas_entrega',
            'video_entrega',
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
            'video_entrega': forms.FileInput(attrs={
                'class': 'mod-input',
                'accept': 'video/mp4,video/webm,video/quicktime,.mp4,.webm,.mov,.m4v',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['checklist_entrega'].initial = self.instance.checklist_entrega

    def save(self, commit=True):
        self.instance.checklist_entrega = list(self.cleaned_data.get('checklist_entrega', []))
        return super().save(commit=commit)

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

    def clean_video_entrega(self):
        video = self.cleaned_data.get('video_entrega')
        validar_video_entrega(video)
        return video


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
