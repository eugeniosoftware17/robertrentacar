from django.shortcuts import render

from .permisos import RUTAS_PUBLICAS, modulo_desde_ruta, modulos_usuario, puede_acceder
from .panel_path import panel_prefix


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
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        return True
