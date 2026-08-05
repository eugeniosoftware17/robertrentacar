"""Permisos del panel por rol (Administrador / Empleado)."""

GRUPO_ADMIN = 'Administrador'
GRUPO_EMPLEADO = 'Empleado'

MODULOS = {
    'dashboard': 'Dashboard',
    'calendario': 'Calendario',
    'vehiculos': 'Vehículos',
    'mantenimiento': 'Mantenimiento',
    'reservas': 'Reservas',
    'clientes': 'Clientes',
    'pagos': 'Pagos',
    'reportes': 'Reportes',
    'sitio_web': 'Sitio web',
    'configuracion': 'Configuración',
}

MODULOS_EMPLEADO_DEFAULT = [
    'dashboard',
    'calendario',
    'reservas',
    'clientes',
    'vehiculos',
    'pagos',
]

RUTAS_PUBLICAS = (
    '/cuentas/login/',
    '/cuentas/logout/',
)


def rutas_modulo():
    from .panel_path import panel_prefix
    base = panel_prefix()
    return (
        (f'{base}vehiculos/', 'vehiculos'),
        (f'{base}clientes/', 'clientes'),
        (f'{base}reservas/', 'reservas'),
        (f'{base}calendario/', 'calendario'),
        (f'{base}mantenimiento/', 'mantenimiento'),
        (f'{base}pagos/', 'pagos'),
        (f'{base}reportes/', 'reportes'),
        (f'{base}sitio/', 'sitio_web'),
        (f'{base}configuracion/', 'configuracion'),
    )


def permiso_codename(modulo):
    return f'modulo_{modulo}'


def permiso_completo(modulo):
    return f'core.{permiso_codename(modulo)}'


def es_admin(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=GRUPO_ADMIN).exists()


def es_empleado(user):
    if not user.is_authenticated:
        return False
    if user.groups.filter(name=GRUPO_EMPLEADO).exists():
        return True
    from .sync_permisos import modulos_desde_permisos
    return bool(modulos_desde_permisos(user)) and not es_admin(user)


def modulos_usuario(user):
    if not user.is_authenticated:
        return []
    if es_admin(user):
        return list(MODULOS.keys())
    from .sync_permisos import modulos_desde_permisos
    return modulos_desde_permisos(user)


def puede_acceder(user, modulo):
    if es_admin(user):
        return True
    return user.has_perm(permiso_completo(modulo))


def modulo_desde_ruta(path):
    from .panel_path import panel_prefix
    base = panel_prefix().rstrip('/')
    for prefijo, modulo in rutas_modulo():
        if path.startswith(prefijo):
            return modulo
    if path in (f'{base}/', base):
        return 'dashboard'
    return None


def rol_usuario(user):
    if not user.is_authenticated:
        return ''
    if es_admin(user):
        return 'Administrador'
    if es_empleado(user):
        return 'Empleado'
    return 'Sin rol'
