from django import forms

from apps.vehiculos.models import Vehiculo

from .models import Empleado, Gasto, PagoNomina


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'apellido', 'puesto', 'telefono', 'email',
            'salario_base', 'fecha_ingreso', 'activo', 'notas',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input'}),
            'apellido': forms.TextInput(attrs={'class': 'mod-input'}),
            'puesto': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Cajero, Mecánico...'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input'}),
            'email': forms.EmailInput(attrs={'class': 'mod-input'}),
            'salario_base': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'notas': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
        }


class PagoNominaForm(forms.ModelForm):
    class Meta:
        model = PagoNomina
        fields = ['empleado', 'concepto', 'monto', 'fecha_pago', 'metodo', 'notas']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'mod-input'}),
            'concepto': forms.Select(attrs={'class': 'mod-input'}),
            'monto': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'metodo': forms.Select(attrs={'class': 'mod-input'}),
            'notas': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['empleado'].queryset = Empleado.objects.filter(activo=True)


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['concepto', 'categoria', 'monto', 'fecha', 'vehiculo', 'notas']
        widgets = {
            'concepto': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Gasolina, publicidad...'}),
            'categoria': forms.Select(attrs={'class': 'mod-input'}),
            'monto': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'fecha': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'vehiculo': forms.Select(attrs={'class': 'mod-input'}),
            'notas': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True)
        self.fields['vehiculo'].required = False
