"""Permisos del panel por rol (Administrador del sistema / Dueño / Empleado)."""

GRUPO_SISTEMA = 'Administrador del sistema'
GRUPO_DUENO = 'Dueño del negocio'
GRUPO_EMPLEADO = 'Empleado'

# Nombre legacy del grupo admin (antes de separar roles).
GRUPO_ADMIN_LEGACY = 'Administrador'

# Alias interno por compatibilidad con imports existentes.
GRUPO_ADMIN = GRUPO_SISTEMA

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

# Solo administradores del sistema (Cloud Tech / superusuario).
MODULOS_SOLO_SISTEMA = [
    'configuracion',
    'sitio_web',
]

# Alias legacy usado en formularios de empleados.
MODULOS_SOLO_ADMIN = MODULOS_SOLO_SISTEMA

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


def es_admin_sistema(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=GRUPO_SISTEMA).exists()


def es_dueno(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=GRUPO_DUENO).exists()


def es_admin(user):
    """Rol elevado del negocio: dueño o administrador del sistema."""
    return es_admin_sistema(user) or es_dueno(user)


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
    if es_admin_sistema(user):
        return list(MODULOS.keys())
    if es_dueno(user):
        return [
            modulo for modulo in MODULOS
            if modulo not in MODULOS_SOLO_SISTEMA
        ]
    from .sync_permisos import modulos_desde_permisos
    return [
        modulo for modulo in modulos_desde_permisos(user)
        if modulo not in MODULOS_SOLO_SISTEMA
    ]


def puede_acceder(user, modulo):
    if modulo in MODULOS_SOLO_SISTEMA and not es_admin_sistema(user):
        return False
    if es_admin_sistema(user):
        return True
    if es_dueno(user):
        return modulo not in MODULOS_SOLO_SISTEMA
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
    if es_admin_sistema(user):
        return GRUPO_SISTEMA
    if es_dueno(user):
        return GRUPO_DUENO
    if es_empleado(user):
        return GRUPO_EMPLEADO
    return 'Sin rol'
