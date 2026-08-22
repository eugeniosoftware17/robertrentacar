from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import AccesoModulo
from .permisos import (
    GRUPO_ADMIN_LEGACY,
    GRUPO_DUENO,
    GRUPO_EMPLEADO,
    GRUPO_SISTEMA,
    MODULOS,
    MODULOS_EMPLEADO_DEFAULT,
    MODULOS_SOLO_SISTEMA,
    permiso_codename,
)


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


def migrar_grupos_legacy():
    """
    Renombra el grupo «Administrador» antiguo y mueve dueños al rol correcto.
    Los superusuarios quedan como admin del sistema; el resto pasa a dueño.
    """
    legacy = Group.objects.filter(name=GRUPO_ADMIN_LEGACY).first()
    if not legacy:
        return

    sistema, _ = Group.objects.get_or_create(name=GRUPO_SISTEMA)
    dueno, _ = Group.objects.get_or_create(name=GRUPO_DUENO)

    for user in legacy.user_set.all():
        user.groups.remove(legacy)
        if user.is_superuser:
            user.groups.add(sistema)
        else:
            user.groups.add(dueno)

    legacy.delete()

    sistema = Group.objects.filter(name=GRUPO_SISTEMA).first()
    dueno = Group.objects.filter(name=GRUPO_DUENO).first()
    if sistema and dueno:
        for user in sistema.user_set.filter(is_superuser=False):
            user.groups.add(dueno)
            user.groups.remove(sistema)


def sincronizar_grupo_sistema():
    grupo, _ = Group.objects.get_or_create(name=GRUPO_SISTEMA)
    grupo.permissions.set(permisos_panel())


def sincronizar_grupo_dueno():
    grupo, _ = Group.objects.get_or_create(name=GRUPO_DUENO)
    modulos = [m for m in MODULOS if m not in MODULOS_SOLO_SISTEMA]
    perms = [_permiso_modulo(m) for m in modulos]
    grupo.permissions.set(perms)


def sincronizar_grupo_empleado():
    grupo, _ = Group.objects.get_or_create(name=GRUPO_EMPLEADO)
    permitidos = [
        modulo for modulo in modulos_empleado_default()
        if modulo not in MODULOS_SOLO_SISTEMA
    ]
    perms = [_permiso_modulo(m) for m in MODULOS if m in permitidos]
    grupo.permissions.set(perms)


def asegurar_accesos_modulo():
    """Crea filas AccesoModulo faltantes con valores por defecto."""
    for clave in MODULOS:
        if clave in MODULOS_SOLO_SISTEMA:
            continue
        permitido = clave in MODULOS_EMPLEADO_DEFAULT
        AccesoModulo.objects.get_or_create(
            modulo=clave,
            defaults={'permitido': permitido},
        )


def sincronizar_permisos_grupos():
    migrar_grupos_legacy()
    asegurar_accesos_modulo()
    sincronizar_grupo_sistema()
    sincronizar_grupo_dueno()
    sincronizar_grupo_empleado()
