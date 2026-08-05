"""Ruta secreta del panel administrativo (no usar /panel/ en producción)."""


def panel_segment():
    from django.conf import settings
    return getattr(settings, 'PANEL_PATH', 'panel').strip('/')


def panel_prefix():
    """Prefijo con barras, ej. /dv-rc-ops/"""
    seg = panel_segment()
    return f'/{seg}/' if seg else '/panel/'


def panel_route(subpath):
    """Ej. panel_route('reservas/') -> /dv-rc-ops/reservas/"""
    return f'{panel_prefix()}{subpath.lstrip("/")}'
