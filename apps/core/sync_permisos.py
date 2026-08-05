from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import AccesoModulo
from .permisos import GRUPO_ADMIN, GRUPO_EMPLEADO, MODULOS, MODULOS_EMPLEADO_DEFAULT, permiso_codename


def _content_type():
    return ContentType.objects.get_for_model(AccesoModulo)


def _permiso_modulo(modulo):
    return Permission.objects.get(
        content_type=_content_type(),
        codename=permiso_codename(modulo),
    )


def permisos_panel():
    """Todos los permisos del panel (core.modulo_*)."""
    return Permission.objects.filter(
        content_type=_content_type(),
        codename__startswith='modulo_',
    )


def modulos_desde_permisos(user):
    """Módulos a los que el usuario tiene permiso (directo o por grupo)."""
    return [
        modulo for modulo in MODULOS
        if user.has_perm(f'core.{permiso_codename(modulo)}')
    ]


def modulos_empleado_default():
    from .models import AccesoModulo

    activos = list(
        AccesoModulo.objects.filter(permitido=True).values_list('modulo', flat=True)
    )
    if activos:
        return activos
    return MODULOS_EMPLEADO_DEFAULT.copy()


def sincronizar_grupo_admin():
    grupo, _ = Group.objects.get_or_create(name=GRUPO_ADMIN)
    grupo.permissions.set(permisos_panel())


def sincronizar_grupo_empleado():
    grupo, _ = Group.objects.get_or_create(name=GRUPO_EMPLEADO)
    permitidos = modulos_empleado_default()
    perms = [_permiso_modulo(m) for m in MODULOS if m in permitidos]
    grupo.permissions.set(perms)


def sincronizar_permisos_grupos():
    sincronizar_grupo_admin()
    sincronizar_grupo_empleado()
