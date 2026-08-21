from django.contrib.auth.middleware import LoginRequiredMiddleware as DjangoLoginRequiredMiddleware
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.urls import reverse
import time

from .permisos import RUTAS_PUBLICAS, modulo_desde_ruta, modulos_usuario, puede_acceder, url_inicio_panel
from .panel_path import panel_prefix

SESSION_ULTIMA_ACTIVIDAD = '_panel_ultima_actividad'

# Subcarpetas de MEDIA_ROOT visibles sin login (sitio web publico).
RUTAS_MEDIA_PUBLICAS = (
    '/media/sitio/',
    '/media/vehiculos/',
)

# Contenido operativo/privado bajo media/ (entregas, devoluciones, previews del panel).
RUTAS_MEDIA_PRIVADAS = (
    '/media/sitio/preview/',
    '/media/reservas/',
)


def es_media_publica(path):
    if any(path.startswith(ruta) for ruta in RUTAS_MEDIA_PRIVADAS):
        return False
    return any(path.startswith(ruta) for ruta in RUTAS_MEDIA_PUBLICAS)


class LoginRequiredMiddleware(DjangoLoginRequiredMiddleware):
    """Exige login salvo vistas @login_not_required y media publica del sitio."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        if es_media_publica(request.path):
            return None
        return super().process_view(request, view_func, view_args, view_kwargs)


class ModuloPermisoMiddleware:
    """Bloquea URLs del panel según el rol del usuario."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._debe_verificar(request):
            if not modulos_usuario(request.user):
                return render(request, 'sin_rol.html', {
                    'page_title': 'Sin acceso',
                }, status=403)

            modulo = modulo_desde_ruta(request.path)
            if modulo and not puede_acceder(request.user, modulo):
                return render(request, '403.html', {
                    'page_title': 'Acceso denegado',
                    'modulo': modulo,
                    'url_inicio_panel': url_inicio_panel(request.user),
                }, status=403)

        return self.get_response(request)

    def _debe_verificar(self, request):
        if not request.path.startswith(panel_prefix()):
            return False
        if not request.user.is_authenticated:
            return False
        if any(request.path.startswith(ruta) for ruta in RUTAS_PUBLICAS):
            return False
        if request.path.startswith('/admin/'):
            return False
        if request.path.startswith('/static/') or es_media_publica(request.path):
            return False
        return True


class InactividadSesionMiddleware:
    """Cierra la sesión si el usuario lleva demasiado tiempo sin actividad."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._aplica(request):
            limite_seg = self._limite_segundos()
            ahora = time.time()
            ultima = request.session.get(SESSION_ULTIMA_ACTIVIDAD)

            if ultima is not None and (ahora - ultima) > limite_seg:
                logout(request)
                login_url = reverse('cuentas:login')
                return redirect(f'{login_url}?inactividad=1')

            request.session[SESSION_ULTIMA_ACTIVIDAD] = ahora

        return self.get_response(request)

    def _aplica(self, request):
        if not request.user.is_authenticated:
            return False
        path = request.path
        if path.startswith('/static/'):
            return False
        if any(path.startswith(ruta) for ruta in RUTAS_PUBLICAS):
            return False
        return True

    def _limite_segundos(self):
        from apps.configuracion.models import ConfiguracionEmpresa

        horas = ConfiguracionEmpresa.obtener().bloqueo_inactividad_horas
        return horas * 3600
