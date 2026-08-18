from datetime import date

from django.utils import timezone


def rango_mes_actual():
    hoy = timezone.localdate()
    return hoy.replace(day=1), hoy


def _parse_fecha(valor):
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return None


def normalizar_rango(desde_str, hasta_str, *, desde_def=None, hasta_def=None):
    """
    Devuelve fechas date normalizadas e ISO para filtros.
    Si desde > hasta, las intercambia.
    """
    desde = _parse_fecha(desde_str) if desde_str else desde_def
    hasta = _parse_fecha(hasta_str) if hasta_str else hasta_def

    invertido = False
    if desde and hasta and desde > hasta:
        desde, hasta = hasta, desde
        invertido = True

    return {
        'desde': desde,
        'hasta': hasta,
        'desde_iso': desde.isoformat() if desde else '',
        'hasta_iso': hasta.isoformat() if hasta else '',
        'invertido': invertido,
        'tiene_rango': bool(desde or hasta),
    }
