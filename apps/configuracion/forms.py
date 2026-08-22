from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from apps.core.models import AccesoModulo
from apps.core.permisos import (
    GRUPO_DUENO,
    GRUPO_EMPLEADO,
    GRUPO_SISTEMA,
    MODULOS,
    MODULOS_SOLO_SISTEMA,
)

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
            if clave in MODULOS_SOLO_SISTEMA:
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
            if clave not in MODULOS_SOLO_SISTEMA
        }
        return cls(initial=initial)

    def guardar(self):
        for clave in MODULOS:
            if clave in MODULOS_SOLO_SISTEMA:
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
    ROL_DUENO = GRUPO_DUENO
    ROL_SISTEMA = GRUPO_SISTEMA

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
            (ROL_DUENO, 'Dueño del negocio'),
            (ROL_SISTEMA, 'Administrador del sistema'),
        ],
        widget=forms.Select(attrs={'class': 'mod-input'}),
    )

    def __init__(self, *args, puede_crear_sistema=True, **kwargs):
        self.puede_crear_sistema = puede_crear_sistema
        super().__init__(*args, **kwargs)
        if not puede_crear_sistema:
            self.fields['rol'].choices = [
                (self.ROL_EMPLEADO, 'Empleado'),
                (self.ROL_DUENO, 'Dueño del negocio'),
            ]

    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if rol == self.ROL_SISTEMA and not self.puede_crear_sistema:
            raise ValidationError('No puedes asignar el rol de administrador del sistema.')
        return rol

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
    ROL_DUENO = GRUPO_DUENO
    ROL_SISTEMA = GRUPO_SISTEMA
    ROL_NINGUNO = 'ninguno'

    rol = forms.ChoiceField(
        label='Rol',
        choices=[
            (ROL_EMPLEADO, 'Empleado'),
            (ROL_DUENO, 'Dueño del negocio'),
            (ROL_SISTEMA, 'Administrador del sistema'),
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

    def __init__(self, *args, usuario=None, puede_asignar_sistema=True, **kwargs):
        self.usuario = usuario
        self.puede_asignar_sistema = puede_asignar_sistema
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['rol'].initial = _rol_actual(usuario)
            self.fields['is_active'].initial = usuario.is_active
        if not puede_asignar_sistema:
            opciones = [
                (self.ROL_EMPLEADO, 'Empleado'),
                (self.ROL_DUENO, 'Dueño del negocio'),
                (self.ROL_NINGUNO, 'Sin rol'),
            ]
            if usuario and _rol_actual(usuario) == self.ROL_SISTEMA:
                opciones.insert(2, (self.ROL_SISTEMA, 'Administrador del sistema'))
            self.fields['rol'].choices = opciones

    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if rol == self.ROL_SISTEMA and not self.puede_asignar_sistema:
            raise ValidationError('No puedes asignar el rol de administrador del sistema.')
        return rol

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
    if user.groups.filter(name=GRUPO_SISTEMA).exists():
        return GRUPO_SISTEMA
    if user.groups.filter(name=GRUPO_DUENO).exists():
        return GRUPO_DUENO
    if user.groups.filter(name=GRUPO_EMPLEADO).exists():
        return GRUPO_EMPLEADO
    return EditarUsuarioPanelForm.ROL_NINGUNO


def _asignar_rol_panel(user, rol):
    sistema = Group.objects.get(name=GRUPO_SISTEMA)
    dueno = Group.objects.get(name=GRUPO_DUENO)
    empleado = Group.objects.get(name=GRUPO_EMPLEADO)
    user.groups.remove(sistema, dueno, empleado)
    user.user_permissions.clear()
    if rol == GRUPO_SISTEMA:
        user.groups.add(sistema)
    elif rol == GRUPO_DUENO:
        user.groups.add(dueno)
    elif rol == GRUPO_EMPLEADO:
        user.groups.add(empleado)
