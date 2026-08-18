from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.vehiculos.models import Vehiculo

from .models import Empleado, Gasto, PagoNomina


def _validar_monto_positivo(monto, campo='monto'):
    if monto is not None and monto <= 0:
        raise ValidationError('El monto debe ser mayor que cero.')
    return monto


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

    def clean_salario_base(self):
        salario = self.cleaned_data.get('salario_base')
        if salario is not None and salario < 0:
            raise ValidationError('El salario base no puede ser negativo.')
        return salario


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
        qs = Empleado.objects.filter(activo=True)
        if self.instance.pk and self.instance.empleado_id:
            qs = Empleado.objects.filter(
                Q(activo=True) | Q(pk=self.instance.empleado_id)
            )
        self.fields['empleado'].queryset = qs.distinct().order_by('-activo', 'apellido', 'nombre')

    def clean_monto(self):
        return _validar_monto_positivo(self.cleaned_data.get('monto'))


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

    def clean_monto(self):
        return _validar_monto_positivo(self.cleaned_data.get('monto'))
