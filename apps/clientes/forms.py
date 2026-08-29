from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'apellido',
            'documento',
            'pasaporte',
            'telefono',
            'email',
            'direccion',
            'nacionalidad',
            'ocupacion',
            'lugar_expedicion',
            'licencia_numero',
            'licencia_vence',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Apellido'}),
            'documento': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '001-0000000-0'}),
            'pasaporte': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Opcional, para extranjeros'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '809-000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'mod-input', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Dirección'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Nacionalidad'}),
            'ocupacion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Ocupación'}),
            'lugar_expedicion': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Lugar de expedición'}),
            'licencia_numero': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Número de licencia'}),
            'licencia_vence': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }
