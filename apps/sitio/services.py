from datetime import date, timedelta

from django.core.cache import cache
from django.utils import timezone

from apps.mantenimiento.models import Mantenimiento
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

RESERVA_LIMITE_INTENTOS = 5
RESERVA_LIMITE_VENTANA_SEGUNDOS = 15 * 60


def ip_cliente(request):
    return request.META.get('REMOTE_ADDR', 'desconocida')


def demasiados_intentos_reserva(request):
    """Freno anti-spam simple por IP: máx. RESERVA_LIMITE_INTENTOS envíos cada 15 min."""
    clave = f'reserva_intentos_{ip_cliente(request)}'
    intentos = cache.get(clave, 0)
    if intentos >= RESERVA_LIMITE_INTENTOS:
        return True
    cache.set(clave, intentos + 1, RESERVA_LIMITE_VENTANA_SEGUNDOS)
    return False


def vehiculos_publicos():
    qs = Vehiculo.objects.filter(activo=True, visible_en_web=True)
    config = None
    from .models import ConfiguracionSitio
    config = ConfiguracionSitio.obtener()
    if config.bloquear_mantenimiento:
        qs = qs.exclude(estado=Vehiculo.Estado.MANTENIMIENTO)
    return qs.prefetch_related('fotos_galeria').order_by('orden_web', 'marca', 'modelo')


def reservas_bloqueantes(vehiculo, excluir_reserva_id=None):
    qs = Reserva.objects.filter(vehiculo=vehiculo).exclude(
        estado=Reserva.Estado.CANCELADA,
    )
    if excluir_reserva_id:
        qs = qs.exclude(pk=excluir_reserva_id)
    return qs


def tiene_conflicto_reserva(vehiculo, fecha_inicio, fecha_fin, excluir_reserva_id=None):
    qs = reservas_bloqueantes(vehiculo, excluir_reserva_id)
    return qs.filter(
        fecha_inicio__lte=fecha_fin,
        fecha_fin__gte=fecha_inicio,
    ).exists()


def vehiculo_reservable(vehiculo):
    if not vehiculo.activo or not vehiculo.visible_en_web:
        return False
    from .models import ConfiguracionSitio
    if ConfiguracionSitio.obtener().bloquear_mantenimiento:
        if vehiculo.estado == Vehiculo.Estado.MANTENIMIENTO:
            return False
    return True


def vehiculos_relacionados(vehiculo, por_grupo=3):
    """Otros vehículos agrupados por criterio (categoría, transmisión, etc.)."""
    base = vehiculos_publicos().exclude(pk=vehiculo.pk)
    vistos = set()
    grupos = []

    def tomar(queryset, titulo, filtro_categoria='', filtro_transmision=''):
        items = []
        for v in queryset:
            if v.pk in vistos:
                continue
            items.append(v)
            vistos.add(v.pk)
            if len(items) >= por_grupo:
                break
        if items:
            grupos.append({
                'titulo': titulo,
                'vehiculos': items,
                'filtro_categoria': filtro_categoria,
                'filtro_transmision': filtro_transmision,
            })

    cat = vehiculo.get_categoria_display()
    trans = vehiculo.get_transmision_display()

    tomar(
        base.filter(categoria=vehiculo.categoria, transmision=vehiculo.transmision),
        f'{cat} · {trans}',
        vehiculo.categoria,
        vehiculo.transmision,
    )
    tomar(
        base.filter(categoria=vehiculo.categoria),
        f'Más {cat}',
        vehiculo.categoria,
        '',
    )
    tomar(
        base.filter(transmision=vehiculo.transmision),
        f'Transmisión {trans}',
        '',
        vehiculo.transmision,
    )
    tomar(base, 'Otros en la flota', '', '')
    return grupos


def fechas_ocupadas(vehiculo, desde: date, hasta: date, excluir_reserva_id=None):
    """Lista de fechas ISO ocupadas por reservas en el rango."""
    ocupadas = set()
    for reserva in reservas_bloqueantes(vehiculo, excluir_reserva_id):
        ini = max(reserva.fecha_inicio, desde)
        fin = min(reserva.fecha_fin, hasta)
        if fin < ini:
            continue
        dia = ini
        while dia <= fin:
            ocupadas.add(dia.isoformat())
            dia += timedelta(days=1)
    return sorted(ocupadas)


def filtrar_por_disponibilidad(queryset, fecha_inicio, fecha_fin):
    if not fecha_inicio or not fecha_fin:
        return queryset
    if fecha_fin < fecha_inicio:
        return queryset.none()
    ids = []
    for vehiculo in queryset:
        if not tiene_conflicto_reserva(vehiculo, fecha_inicio, fecha_fin):
            ids.append(vehiculo.pk)
    return queryset.filter(pk__in=ids)


def validar_anticipacion(fecha_inicio):
    from .models import ConfiguracionSitio
    config = ConfiguracionSitio.obtener()
    minimo = timezone.localdate() + timedelta(hours=config.anticipacion_horas)
    # anticipacion en horas pero fechas son date — comparar inicio >= hoy + 1 si 24h
    if config.anticipacion_horas >= 24:
        min_date = timezone.localdate() + timedelta(days=config.anticipacion_horas // 24)
    else:
        min_date = timezone.localdate()
    if fecha_inicio < min_date:
        return False, min_date
    return True, min_date


def bloques_mantenimiento_dia(vehiculo, desde: date, hasta: date):
    """Fechas con mantenimiento programado/en proceso (bloqueo opcional por día)."""
    from .models import ConfiguracionSitio
    if not ConfiguracionSitio.obtener().bloquear_mantenimiento:
        return []
    bloqueadas = set()
    qs = Mantenimiento.objects.filter(
        vehiculo=vehiculo,
        estado__in=[Mantenimiento.Estado.PROGRAMADO, Mantenimiento.Estado.EN_PROCESO],
        fecha__gte=desde,
        fecha__lte=hasta,
    )
    for m in qs:
        bloqueadas.add(m.fecha.isoformat())
    return sorted(bloqueadas)
