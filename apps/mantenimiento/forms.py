from django import forms

from apps.vehiculos.models import Vehiculo

from .models import Mantenimiento


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = [
            'vehiculo', 'fecha', 'tipo', 'estado', 'costo',
            'kilometraje', 'descripcion', 'proximo_servicio',
        ]
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'mod-input'}),
            'fecha': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'mod-input'}),
            'estado': forms.Select(attrs={'class': 'mod-input'}),
            'costo': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'descripcion': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
            'proximo_servicio': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True)
