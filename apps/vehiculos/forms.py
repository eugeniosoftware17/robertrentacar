from django import forms

from .models import CategoriaVehiculo, Vehiculo


class CategoriaVehiculoForm(forms.ModelForm):
    class Meta:
        model = CategoriaVehiculo
        fields = ['nombre', 'slug', 'activa', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'SUV'}),
            'slug': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'suv (opcional, se genera solo)'}),
            'orden': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'activa': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            'marca',
            'modelo',
            'anio',
            'placa',
            'categoria',
            'transmision',
            'tarifa_diaria',
            'precio_compra',
            'fecha_compra',
            'estado',
            'color',
            'kilometraje',
            'foto',
            'foto_url',
            'descripcion_web',
            'descripcion_web_en',
            'visible_en_web',
            'destacado_web',
            'orden_web',
            'seguro_vence',
            'prox_mantenimiento',
            'activo',
        ]
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Corolla'}),
            'anio': forms.NumberInput(attrs={'class': 'mod-input', 'min': 1990, 'max': 2030}),
            'placa': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'A123456'}),
            'categoria': forms.Select(attrs={'class': 'mod-input'}),
            'transmision': forms.Select(attrs={'class': 'mod-input'}),
            'tarifa_diaria': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'mod-input', 'step': '0.01', 'min': '0'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'mod-input'}),
            'color': forms.TextInput(attrs={'class': 'mod-input', 'placeholder': 'Blanco'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'foto': forms.FileInput(attrs={'class': 'mod-input'}),
            'foto_url': forms.URLInput(attrs={'class': 'mod-input', 'placeholder': 'https://...'}),
            'descripcion_web': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
            'descripcion_web_en': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 3}),
            'visible_en_web': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'destacado_web': forms.CheckboxInput(attrs={'class': 'mod-check'}),
            'orden_web': forms.NumberInput(attrs={'class': 'mod-input', 'min': '0'}),
            'seguro_vence': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'prox_mantenimiento': forms.DateInput(attrs={'class': 'mod-input', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'mod-check'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaVehiculo.objects.filter(activa=True).order_by('orden', 'nombre')
        if not self.fields['categoria'].queryset.exists():
            self.fields['categoria'].queryset = CategoriaVehiculo.objects.all().order_by('orden', 'nombre')
