from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'apellido',
            'documento',
            'telefono',
            'email',
            'licencia_numero',
            'licencia_vence',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Apellido'}),
            'documento': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '001-0000000-0'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': '809-000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'mod-input', 'placeholder': 'correo@ejemplo.com'}),
            'licencia_numero': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Número de licencia'}),
            'licencia_vence': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }
