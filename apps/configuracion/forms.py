from django import forms

from apps.core.models import AccesoModulo
from apps.core.permisos import MODULOS

from .models import ConfiguracionEmpresa


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEmpresa
        fields = ['nombre', 'telefono', 'email', 'direccion', 'rnc', 'notas_contrato']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input'}),
            'email': forms.EmailInput(attrs={'class': 'mod-input'}),
            'direccion': forms.TextInput(attrs={'class': 'mod-input'}),
            'rnc': forms.TextInput(attrs={'class': 'mod-input'}),
            'notas_contrato': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 5}),
        }


class PermisosEmpleadoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for clave, etiqueta in MODULOS.items():
            self.fields[clave] = forms.BooleanField(
                label=etiqueta,
                required=False,
            )

    @classmethod
    def desde_bd(cls):
        accesos = {a.modulo: a.permitido for a in AccesoModulo.objects.all()}
        initial = {clave: accesos.get(clave, False) for clave in MODULOS}
        return cls(initial=initial)

    def guardar(self):
        for clave in MODULOS:
            permitido = self.cleaned_data.get(clave, False)
            AccesoModulo.objects.update_or_create(
                modulo=clave,
                defaults={'permitido': permitido},
            )
        from apps.core.sync_permisos import sincronizar_grupo_empleado
        sincronizar_grupo_empleado()
