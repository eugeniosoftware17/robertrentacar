from functools import wraps

from django.shortcuts import render

from .permisos import puede_acceder


def requiere_modulo(modulo):
    """Decorador opcional para vistas que no pasan por el middleware de rutas."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not puede_acceder(request.user, modulo):
                return render(request, '403.html', {
                    'page_title': 'Acceso denegado',
                    'modulo': modulo,
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
