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
    'finanzas': 'Nómina y gastos',
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

# Solo administradores (nunca se delega al grupo Empleado).
MODULOS_SOLO_ADMIN = [
    'configuracion',
]

ORDEN_INICIO_PANEL = [
    'dashboard',
    'calendario',
    'reservas',
    'clientes',
    'vehiculos',
    'pagos',
    'mantenimiento',
    'reportes',
    'finanzas',
    'sitio_web',
    'configuracion',
]

URLS_MODULO_PANEL = {
    'dashboard': 'dashboard',
    'calendario': 'calendario:index',
    'vehiculos': 'vehiculos:lista',
    'mantenimiento': 'mantenimiento:lista',
    'reservas': 'reservas:lista',
    'clientes': 'clientes:lista',
    'pagos': 'pagos:lista',
    'reportes': 'reportes:index',
    'sitio_web': 'sitio_web:panel_index',
    'finanzas': 'finanzas:index',
    'configuracion': 'configuracion:index',
}

RUTAS_PUBLICAS = (
    '/login/',
    '/logout/',
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
        (f'{base}finanzas/', 'finanzas'),
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
    return [
        modulo for modulo in modulos_desde_permisos(user)
        if modulo not in MODULOS_SOLO_ADMIN
    ]


def puede_acceder(user, modulo):
    if modulo in MODULOS_SOLO_ADMIN and not es_admin(user):
        return False
    if es_admin(user):
        return True
    return user.has_perm(permiso_completo(modulo))


def url_inicio_panel(user):
    from django.urls import NoReverseMatch, reverse

    for modulo in ORDEN_INICIO_PANEL:
        if modulo in modulos_usuario(user):
            nombre = URLS_MODULO_PANEL.get(modulo)
            if not nombre:
                continue
            try:
                return reverse(nombre)
            except NoReverseMatch:
                continue
    return reverse('cuentas:login')


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
