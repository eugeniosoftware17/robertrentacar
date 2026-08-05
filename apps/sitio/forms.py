from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

from .models import ConfiguracionSitio, PaginaInformativa
from .services import tiene_conflicto_reserva, validar_anticipacion, vehiculo_reservable


class ReservaWebForm(forms.Form):
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.none(),
        widget=forms.HiddenInput,
    )
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'sitio-input'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'sitio-input'}))
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'sitio-input'}))
    apellido = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'sitio-input'}))
    documento = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'sitio-input'}))
    telefono = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'sitio-input'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'sitio-input'}))
    licencia_numero = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'sitio-input'}))
    licencia_vence = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'sitio-input'}))
    notas = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'sitio-input', 'rows': 3}))

    def __init__(self, *args, vehiculo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vehiculo_fijo = vehiculo
        if vehiculo:
            self.fields['vehiculo'].initial = vehiculo
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(pk=vehiculo.pk)

    def clean_vehiculo(self):
        vehiculo = self.cleaned_data.get('vehiculo') or self.vehiculo_fijo
        if not vehiculo or not vehiculo_reservable(vehiculo):
            raise ValidationError('Este vehículo no está disponible para reserva en línea.')
        return vehiculo

    def clean(self):
        cleaned = super().clean()
        vehiculo = cleaned.get('vehiculo')
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_fin = cleaned.get('fecha_fin')
        licencia_vence = cleaned.get('licencia_vence')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de fin debe ser posterior al inicio.'})

        if fecha_inicio:
            ok, min_date = validar_anticipacion(fecha_inicio)
            if not ok:
                raise ValidationError({
                    'fecha_inicio': f'La reserva debe iniciar como mínimo el {min_date.strftime("%d/%m/%Y")}.',
                })

        if licencia_vence and licencia_vence < timezone.localdate():
            raise ValidationError({'licencia_vence': 'La licencia está vencida.'})

        if vehiculo and fecha_inicio and fecha_fin:
            if tiene_conflicto_reserva(vehiculo, fecha_inicio, fecha_fin):
                raise ValidationError('El vehículo no está disponible en esas fechas.')

        return cleaned

    def guardar_reserva(self):
        from apps.configuracion.models import ConfiguracionEmpresa

        data = self.cleaned_data
        vehiculo = data['vehiculo']
        documento = data['documento'].strip()

        cliente, _ = Cliente.objects.update_or_create(
            documento=documento,
            defaults={
                'nombre': data['nombre'].strip(),
                'apellido': data['apellido'].strip(),
                'telefono': data['telefono'].strip(),
                'email': (data.get('email') or '').strip(),
                'licencia_numero': data['licencia_numero'].strip(),
                'licencia_vence': data['licencia_vence'],
                'activo': True,
            },
        )

        config = ConfiguracionSitio.obtener()
        estado = (
            Reserva.Estado.CONFIRMADA
            if config.reserva_auto_confirmar
            else Reserva.Estado.PENDIENTE
        )

        notas = (data.get('notas') or '').strip()
        if notas:
            notas = f'[Web] {notas}'
        else:
            notas = '[Web] Reserva desde sitio público'

        reserva = Reserva(
            cliente=cliente,
            vehiculo=vehiculo,
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            estado=estado,
            origen=Reserva.Origen.WEB,
            notas=notas,
            deposito=0,
            requiere_contacto_web=True,
        )
        reserva.full_clean()
        reserva.save()
        ConfiguracionEmpresa.obtener()
        return reserva


class ConfiguracionSitioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSitio
        fields = [
            'home_titulo',
            'home_subtitulo',
            'home_texto',
            'whatsapp',
            'whatsapp_mensaje',
            'whatsapp_flotante',
            'mostrar_whatsapp',
            'horario',
            'instagram',
            'mostrar_instagram',
            'facebook',
            'mostrar_facebook',
            'tiktok',
            'mostrar_tiktok',
            'youtube',
            'mostrar_youtube',
            'twitter',
            'mostrar_twitter',
            'reserva_auto_confirmar',
            'anticipacion_horas',
            'bloquear_mantenimiento',
            'mensaje_reserva_exito',
            'meta_descripcion',
        ]
        widgets = {
            'home_titulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_subtitulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_texto': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 4}),
            'whatsapp': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '+1 809 555 1234'}),
            'whatsapp_mensaje': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 2}),
            'horario': forms.TextInput(attrs={'class': 'mod-input'}),
            'instagram': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://instagram.com/...'}),
            'facebook': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://facebook.com/...'}),
            'tiktok': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://tiktok.com/@...'}),
            'youtube': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://youtube.com/@...'}),
            'twitter': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://x.com/...'}),
            'anticipacion_horas': forms.NumberInput(attrs={'class': 'mod-input', 'min': 0}),
            'mensaje_reserva_exito': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
            'meta_descripcion': forms.TextInput(attrs={'class': 'mod-input', 'maxlength': 160}),
            'whatsapp_flotante': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_whatsapp': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_instagram': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_facebook': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_tiktok': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_youtube': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_twitter': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'reserva_auto_confirmar': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'bloquear_mantenimiento': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }


class PaginaInformativaForm(forms.ModelForm):
    class Meta:
        model = PaginaInformativa
        fields = ['slug', 'titulo', 'contenido', 'publicada', 'en_menu', 'orden']
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'mod-input'}),
            'titulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'contenido': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 12}),
            'orden': forms.NumberInput(attrs={'class': 'mod-input', 'min': 0}),
            'publicada': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'en_menu': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }
