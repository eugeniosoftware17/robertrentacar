from django.db.models import CharField, Q
from django.db.models.functions import Cast

from .models import Vehiculo

CAMPOS_TEXTO = (
    'marca',
    'modelo',
    'placa',
    'slug',
    'color',
    'descripcion_web',
    'descripcion_web_en',
    'foto_url',
    'transmision',
    'estado',
)

CAMPOS_NUMERICOS = (
    'anio',
    'kilometraje',
    'tarifa_diaria',
    'precio_compra',
    'orden_web',
)

CAMPOS_FECHA = (
    'seguro_vence',
    'prox_mantenimiento',
    'fecha_compra',
)


def _q_por_etiquetas_choices(termino, choices, campo):
    q = Q()
    termino_lower = termino.lower()
    for value, label in choices:
        if termino_lower in label.lower() or termino_lower in value.lower():
            q |= Q(**{campo: value})
    return q


def _q_por_palabras_booleanas(termino):
    q = Q()
    termino_lower = termino.lower()
    if termino_lower in {'activo', 'activos', 'si', 'sí'}:
        q |= Q(activo=True)
    if termino_lower in {'inactivo', 'inactivos'}:
        q |= Q(activo=False)
    if termino_lower in {'web', 'sitio', 'publico', 'público', 'visible'}:
        q |= Q(visible_en_web=True)
    if 'destacado' in termino_lower:
        q |= Q(destacado_web=True)
    if termino_lower in {'disponible', 'rentado', 'mantenimiento', 'manual', 'automatico', 'automático', 'cvt'}:
        q |= _q_por_etiquetas_choices(termino, Vehiculo.Estado.choices, 'estado')
        q |= _q_por_etiquetas_choices(termino, Vehiculo.Transmision.choices, 'transmision')
    return q


def _anotar_campos_buscables(qs):
    anotaciones = {
        f'buscar_{campo}': Cast(campo, CharField())
        for campo in (*CAMPOS_NUMERICOS, *CAMPOS_FECHA)
    }
    return qs.annotate(**anotaciones)


def _q_por_termino(termino):
    q = Q()
    for campo in CAMPOS_TEXTO:
        q |= Q(**{f'{campo}__icontains': termino})

    q |= Q(categoria__nombre__icontains=termino)
    q |= Q(categoria__slug__icontains=termino)
    q |= _q_por_etiquetas_choices(termino, Vehiculo.Estado.choices, 'estado')
    q |= _q_por_etiquetas_choices(termino, Vehiculo.Transmision.choices, 'transmision')
    q |= _q_por_palabras_booleanas(termino)

    if termino.isdigit():
        q |= Q(pk=int(termino))

    ref = termino.upper().replace(' ', '')
    if ref.startswith('VEH-') and ref[4:].isdigit():
        q |= Q(pk=int(ref[4:]))

    for campo in CAMPOS_NUMERICOS:
        q |= Q(**{f'buscar_{campo}__icontains': termino})
    for campo in CAMPOS_FECHA:
        q |= Q(**{f'buscar_{campo}__icontains': termino})

    return q


def _q_por_letra(letra):
    q = Q()
    for campo in ('marca', 'modelo', 'placa', 'color', 'slug'):
        q |= Q(**{f'{campo}__istartswith': letra})

    q |= Q(categoria__nombre__istartswith=letra)
    q |= Q(categoria__slug__istartswith=letra)
    q |= _q_por_etiquetas_choices(letra, Vehiculo.Estado.choices, 'estado')
    q |= _q_por_etiquetas_choices(letra, Vehiculo.Transmision.choices, 'transmision')

    for campo in CAMPOS_NUMERICOS:
        q |= Q(**{f'buscar_{campo}__istartswith': letra})
    for campo in CAMPOS_FECHA:
        q |= Q(**{f'buscar_{campo}__istartswith': letra})

    return q


def filtrar_vehiculos(qs, termino='', letra=''):
    termino = (termino or '').strip()
    letra = (letra or '').strip()[:1].upper()

    if termino or letra:
        qs = _anotar_campos_buscables(qs)

    if letra:
        qs = qs.filter(_q_por_letra(letra))

    if termino:
        qs = qs.filter(_q_por_termino(termino))

    return qs.distinct()
