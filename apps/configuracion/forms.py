from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from apps.core.models import AccesoModulo
from apps.core.permisos import GRUPO_ADMIN, GRUPO_EMPLEADO, MODULOS, MODULOS_SOLO_ADMIN

from .models import ConfiguracionEmpresa

User = get_user_model()


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEmpresa
        fields = [
            'nombre', 'telefono', 'email', 'direccion', 'ciudad', 'rnc',
            'bloqueo_inactividad_horas', 'notas_contrato',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mod-input'}),
            'telefono': forms.TextInput(attrs={'class': 'mod-input'}),
            'email': forms.EmailInput(attrs={'class': 'mod-input'}),
            'direccion': forms.TextInput(attrs={'class': 'mod-input'}),
            'ciudad': forms.TextInput(attrs={'class': 'mod-input'}),
            'rnc': forms.TextInput(attrs={'class': 'mod-input'}),
            'bloqueo_inactividad_horas': forms.NumberInput(attrs={
                'class': 'mod-input',
                'min': 1,
                'max': 168,
                'step': 1,
            }),
            'notas_contrato': forms.Textarea(attrs={'class': 'mod-input mod-textarea', 'rows': 5}),
        }


class PermisosEmpleadoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for clave, etiqueta in MODULOS.items():
            if clave in MODULOS_SOLO_ADMIN:
                continue
            self.fields[clave] = forms.BooleanField(
                label=etiqueta,
                required=False,
            )

    @classmethod
    def desde_bd(cls):
        from apps.core.sync_permisos import modulos_empleado_default

        permitidos = set(modulos_empleado_default())
        initial = {
            clave: clave in permitidos
            for clave in MODULOS
            if clave not in MODULOS_SOLO_ADMIN
        }
        return cls(initial=initial)

    def guardar(self):
        for clave in MODULOS:
            if clave in MODULOS_SOLO_ADMIN:
                AccesoModulo.objects.filter(modulo=clave).update(permitido=False)
                continue
            permitido = self.cleaned_data.get(clave, False)
            AccesoModulo.objects.update_or_create(
                modulo=clave,
                defaults={'permitido': permitido},
            )
        from apps.core.sync_permisos import sincronizar_grupo_empleado
        sincronizar_grupo_empleado()


class CrearUsuarioPanelForm(forms.Form):
    ROL_EMPLEADO = GRUPO_EMPLEADO
    ROL_ADMIN = GRUPO_ADMIN

    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'mod-input', 'autocomplete': 'username'}),
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'mod-input'}),
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'mod-input'}),
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'mod-input', 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'mod-input', 'autocomplete': 'new-password'}),
    )
    rol = forms.ChoiceField(
        label='Rol',
        choices=[
            (ROL_EMPLEADO, 'Empleado'),
            (ROL_ADMIN, 'Administrador'),
        ],
        widget=forms.Select(attrs={'class': 'mod-input'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Ese nombre de usuario ya existe.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Las contraseñas no coinciden.')
        if p1 and len(p1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return cleaned

    def guardar(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data.get('first_name', '').strip(),
            last_name=self.cleaned_data.get('last_name', '').strip(),
        )
        _asignar_rol_panel(user, self.cleaned_data['rol'])
        return user


class EditarUsuarioPanelForm(forms.Form):
    ROL_EMPLEADO = GRUPO_EMPLEADO
    ROL_ADMIN = GRUPO_ADMIN
    ROL_NINGUNO = 'ninguno'

    rol = forms.ChoiceField(
        label='Rol',
        choices=[
            (ROL_EMPLEADO, 'Empleado'),
            (ROL_ADMIN, 'Administrador'),
            (ROL_NINGUNO, 'Sin rol'),
        ],
        widget=forms.Select(attrs={'class': 'mod-input'}),
    )
    is_active = forms.BooleanField(
        label='Usuario activo',
        required=False,
        initial=True,
    )
    password1 = forms.CharField(
        label='Nueva contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'mod-input', 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'mod-input', 'autocomplete': 'new-password'}),
    )

    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['rol'].initial = _rol_actual(usuario)
            self.fields['is_active'].initial = usuario.is_active

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise ValidationError('Las contraseñas no coinciden.')
            if p1 and len(p1) < 8:
                raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return cleaned

    def guardar(self):
        user = self.usuario
        user.is_active = self.cleaned_data.get('is_active', False)
        user.save(update_fields=['is_active'])
        _asignar_rol_panel(user, self.cleaned_data['rol'])
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user


def _rol_actual(user):
    if user.groups.filter(name=GRUPO_ADMIN).exists():
        return GRUPO_ADMIN
    if user.groups.filter(name=GRUPO_EMPLEADO).exists():
        return GRUPO_EMPLEADO
    return EditarUsuarioPanelForm.ROL_NINGUNO


def _asignar_rol_panel(user, rol):
    admin = Group.objects.get(name=GRUPO_ADMIN)
    empleado = Group.objects.get(name=GRUPO_EMPLEADO)
    user.groups.remove(admin, empleado)
    user.user_permissions.clear()
    if rol == GRUPO_ADMIN:
        user.groups.add(admin)
    elif rol == GRUPO_EMPLEADO:
        user.groups.add(empleado)
