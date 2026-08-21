from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

from .i18n import IDIOMA_DEFECTO, texto
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
    # Honeypot: campo invisible para personas, atractivo para bots. Si llega lleno, es spam.
    empresa_web = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'sitio-hp', 'tabindex': '-1', 'autocomplete': 'off'}),
    )

    CAMPO_A_CLAVE_TEXTO = {
        'vehiculo': 'res_campo_vehiculo',
        'fecha_inicio': 'res_campo_fecha_inicio',
        'fecha_fin': 'res_campo_fecha_fin',
        'nombre': 'res_campo_nombre',
        'apellido': 'res_campo_apellido',
        'documento': 'res_campo_documento',
        'telefono': 'res_campo_telefono',
        'email': 'res_campo_email',
        'licencia_numero': 'res_campo_licencia_numero',
        'licencia_vence': 'res_campo_licencia_vence',
        'notas': 'res_campo_notas',
    }

    def __init__(self, *args, vehiculo=None, idioma=IDIOMA_DEFECTO, **kwargs):
        super().__init__(*args, **kwargs)
        self.vehiculo_fijo = vehiculo
        if vehiculo:
            self.fields['vehiculo'].initial = vehiculo
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(pk=vehiculo.pk)
        if idioma == 'en':
            for campo, clave in self.CAMPO_A_CLAVE_TEXTO.items():
                if campo in self.fields:
                    self.fields[campo].label = texto(clave, idioma)

    def clean_empresa_web(self):
        valor = self.cleaned_data.get('empresa_web')
        if valor:
            raise ValidationError('No se pudo procesar la solicitud.')
        return valor

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
        telefono = data['telefono'].strip()
        email = (data.get('email') or '').strip()

        cliente, creado = Cliente.objects.get_or_create(
            documento=documento,
            defaults={
                'nombre': data['nombre'].strip(),
                'apellido': data['apellido'].strip(),
                'telefono': telefono,
                'email': email,
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

        if not creado:
            # No pisamos los datos de un cliente ya existente (podría no ser
            # la misma persona que llenó el formulario). Si los datos de
            # contacto llegaron distintos, lo dejamos anotado para el staff.
            if (telefono and telefono != cliente.telefono) or (email and email != cliente.email):
                notas += (
                    f' | Contacto informado en el formulario: tel. {telefono or "—"}, '
                    f'email {email or "—"} (verificar antes de actualizar el cliente).'
                )

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
    CAMPOS_SOLO_ADMIN = ('home_html_extra', 'css_global', 'js_global')

    quitar_home_fondo = forms.BooleanField(
        required=False,
        label='Quitar imagen de fondo actual',
    )
    quitar_logo = forms.BooleanField(
        required=False,
        label='Quitar logo actual',
    )
    quitar_favicon = forms.BooleanField(
        required=False,
        label='Quitar icono del navegador',
    )

    def __init__(self, *args, restringir_avanzado=False, **kwargs):
        super().__init__(*args, **kwargs)
        if restringir_avanzado:
            for campo in self.CAMPOS_SOLO_ADMIN:
                self.fields.pop(campo, None)

    class Meta:
        model = ConfiguracionSitio
        fields = [
            'logo',
            'favicon',
            'mostrar_nombre_junto_logo',
            'home_titulo',
            'home_titulo_en',
            'home_subtitulo',
            'home_subtitulo_en',
            'home_texto',
            'home_texto_en',
            'home_diseno',
            'home_fondo_imagen',
            'home_fondo_posicion',
            'home_fondo_tamano',
            'home_fondo_opacidad',
            'home_mostrar_panel',
            'home_mostrar_categorias',
            'home_mostrar_destacados',
            'home_mostrar_cta',
            'home_mostrar_contador',
            'home_mostrar_redes_hero',
            'servicio_24h',
            'entrega_aeropuertos',
            'mostrar_resenas',
            'resena_calificacion',
            'resena_cantidad',
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
            'mensaje_reserva_exito_en',
            'meta_descripcion',
            'meta_descripcion_en',
            'home_html_extra',
            'css_global',
            'js_global',
        ]
        widgets = {
            'logo': forms.ClearableFileInput(attrs={'class': 'mod-input'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'mod-input', 'accept': '.png,.ico,.webp,.jpg,.jpeg,.svg'}),
            'mostrar_nombre_junto_logo': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_titulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_titulo_en': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_subtitulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_subtitulo_en': forms.TextInput(attrs={'class': 'mod-input'}),
            'home_texto': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 4}),
            'home_texto_en': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 4}),
            'home_diseno': forms.Select(attrs={'class': 'mod-input'}),
            'home_fondo_imagen': forms.ClearableFileInput(attrs={'class': 'mod-input'}),
            'home_fondo_posicion': forms.RadioSelect,
            'home_fondo_tamano': forms.Select(attrs={'class': 'mod-input'}),
            'home_fondo_opacidad': forms.NumberInput(attrs={'class': 'mod-input', 'min': 0, 'max': 100}),
            'home_mostrar_panel': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_mostrar_categorias': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_mostrar_destacados': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_mostrar_cta': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_mostrar_contador': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'home_mostrar_redes_hero': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'servicio_24h': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'entrega_aeropuertos': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'mostrar_resenas': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'resena_calificacion': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.1', 'min': 0, 'max': 5}),
            'resena_cantidad': forms.NumberInput(attrs={'class': 'mod-input', 'min': 0}),
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
            'mensaje_reserva_exito_en': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
            'meta_descripcion': forms.TextInput(attrs={'class': 'mod-input', 'maxlength': 160}),
            'meta_descripcion_en': forms.TextInput(attrs={'class': 'mod-input', 'maxlength': 160}),
            'home_html_extra': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 6}),
            'css_global': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 8}),
            'js_global': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 8}),
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

    def clean_home_fondo_opacidad(self):
        valor = self.cleaned_data.get('home_fondo_opacidad')
        if valor is not None and not 0 <= valor <= 100:
            raise forms.ValidationError('Debe estar entre 0 y 100.')
        return valor

    def clean_favicon(self):
        import os

        archivo = self.cleaned_data.get('favicon')
        if not archivo:
            return archivo
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in {'.png', '.ico', '.webp', '.jpg', '.jpeg', '.svg'}:
            raise ValidationError('Usa PNG, ICO, WebP, JPG o SVG.')
        return archivo


class PaginaInformativaForm(forms.ModelForm):
    CAMPOS_SOLO_ADMIN = ('css_extra', 'js_extra')

    def __init__(self, *args, restringir_avanzado=False, **kwargs):
        super().__init__(*args, **kwargs)
        if restringir_avanzado:
            for campo in self.CAMPOS_SOLO_ADMIN:
                self.fields.pop(campo, None)

    class Meta:
        model = PaginaInformativa
        fields = [
            'slug', 'titulo', 'titulo_en', 'contenido', 'contenido_en',
            'css_extra', 'js_extra', 'publicada', 'en_menu', 'orden',
        ]
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'mod-input'}),
            'titulo': forms.TextInput(attrs={'class': 'mod-input'}),
            'titulo_en': forms.TextInput(attrs={'class': 'mod-input'}),
            'contenido': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 14}),
            'contenido_en': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 14}),
            'css_extra': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 8}),
            'js_extra': forms.Textarea(attrs={'class': 'mod-input mod-textarea mod-code', 'rows': 8}),
            'orden': forms.NumberInput(attrs={'class': 'mod-input', 'min': 0}),
            'publicada': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'en_menu': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }
