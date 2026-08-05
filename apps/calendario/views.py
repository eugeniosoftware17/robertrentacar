import calendar
from datetime import date, timedelta

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

MESES = [
    '',
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
DIAS_SEMANA_LARGO = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

ESTADO_CLASE = {
    Reserva.Estado.PENDIENTE: 'pendiente',
    Reserva.Estado.CONFIRMADA: 'confirmada',
    Reserva.Estado.ACTIVA: 'activa',
    Reserva.Estado.COMPLETADA: 'completada',
}

PAGO_CLASE = {
    'pagado': 'pagado',
    'parcial': 'parcial',
    'pendiente': 'pendiente',
}

PALETA_VEHICULO = [
    '#0b5a60', '#1f7a55', '#96702a', '#5b4d8a', '#a33a3e',
    '#2563eb', '#c2410c', '#7c3aed', '#0891b2', '#be185d',
]


def _color_vehiculo(vehiculo_id):
    return PALETA_VEHICULO[vehiculo_id % len(PALETA_VEHICULO)]


def _rango_mes(anio, mes):
    primer_dia = date(anio, mes, 1)
    if mes == 12:
        ultimo_dia = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
    return primer_dia, ultimo_dia


def _mes_anterior(anio, mes):
    if mes == 1:
        return anio - 1, 12
    return anio, mes - 1


def _mes_siguiente(anio, mes):
    if mes == 12:
        return anio + 1, 1
    return anio, mes + 1


def _semana_lunes(fecha):
    return fecha - timedelta(days=fecha.weekday())


def _query_string(estado='', vehiculo='', cliente='', vista='mes'):
    partes = []
    if estado:
        partes.append(f'estado={estado}')
    if vehiculo:
        partes.append(f'vehiculo={vehiculo}')
    if cliente:
        partes.append(f'cliente={cliente}')
    if vista and vista != 'mes':
        partes.append(f'vista={vista}')
    return '&' + '&'.join(partes) if partes else ''


def _evento_desde_reserva(reserva, dia_actual):
    if reserva.fecha_inicio == dia_actual:
        tipo_dia = 'entrega'
    elif reserva.fecha_fin == dia_actual:
        tipo_dia = 'devolucion'
    else:
        tipo_dia = 'continua'

    return {
        'id': reserva.pk,
        'cliente': reserva.cliente.nombre_completo,
        'vehiculo': reserva.vehiculo.nombre_corto,
        'placa': reserva.vehiculo.placa,
        'vehiculo_id': reserva.vehiculo_id,
        'vehiculo_color': _color_vehiculo(reserva.vehiculo_id),
        'estado': reserva.get_estado_display(),
        'estado_clase': ESTADO_CLASE.get(reserva.estado, 'pendiente'),
        'estado_pago': reserva.estado_pago,
        'estado_pago_label': reserva.estado_pago_label,
        'pago_clase': PAGO_CLASE.get(reserva.estado_pago, 'pendiente'),
        'tipo_dia': tipo_dia,
        'inicio': reserva.fecha_inicio == dia_actual,
        'fin': reserva.fecha_fin == dia_actual,
        'fecha_inicio': reserva.fecha_inicio.isoformat(),
        'fecha_fin': reserva.fecha_fin.isoformat(),
        'precio_total': float(reserva.precio_total),
        'total_pagado': float(reserva.total_pagado),
        'saldo_pendiente': float(reserva.saldo_pendiente),
        'dias': reserva.dias,
        'editar_url': reverse('reservas:editar', args=[reserva.pk]),
        'pago_url': reverse('pagos:crear') + f'?reserva={reserva.pk}',
        'contrato_url': reverse('reservas:contrato', args=[reserva.pk]),
        'entrega_url': reverse('reservas:entrega', args=[reserva.pk]),
        'devolucion_url': reverse('reservas:devolucion', args=[reserva.pk]),
        'puede_entrega': reserva.puede_registrar_entrega and not reserva.entrega_registrada,
        'puede_devolucion': (
            reserva.puede_registrar_devolucion
            and reserva.entrega_registrada
            and not reserva.devolucion_registrada
        ),
    }


def _construir_gantt(reservas, primer_dia, ultimo_dia, vehiculos):
    dias_en_mes = (ultimo_dia - primer_dia).days + 1
    reservas_por_vehiculo = {}

    for reserva in reservas:
        inicio = max(reserva.fecha_inicio, primer_dia)
        fin = min(reserva.fecha_fin, ultimo_dia)
        if fin < inicio:
            continue
        col_start = (inicio - primer_dia).days + 1
        col_span = (fin - inicio).days + 1
        reservas_por_vehiculo.setdefault(reserva.vehiculo_id, []).append({
            'id': reserva.pk,
            'col_start': col_start,
            'col_span': col_span,
            'label': reserva.cliente.nombre_completo,
            'vehiculo': reserva.vehiculo.nombre_corto,
            'placa': reserva.vehiculo.placa,
            'estado_clase': ESTADO_CLASE.get(reserva.estado, 'pendiente'),
            'vehiculo_color': _color_vehiculo(reserva.vehiculo_id),
            'pago_clase': PAGO_CLASE.get(reserva.estado_pago, 'pendiente'),
            'editar_url': reverse('reservas:editar', args=[reserva.pk]),
            'tooltip': (
                f'{reserva.cliente.nombre_completo} · {reserva.vehiculo.placa} · '
                f'{reserva.fecha_inicio.strftime("%d/%m")}–{reserva.fecha_fin.strftime("%d/%m")}'
            ),
        })

    filas = []
    for vehiculo in vehiculos:
        filas.append({
            'vehiculo': vehiculo,
            'barras': reservas_por_vehiculo.get(vehiculo.pk, []),
        })

    dias_cabecera = []
    for i in range(dias_en_mes):
        fecha_dia = primer_dia + timedelta(days=i)
        dias_cabecera.append({
            'numero': fecha_dia.day,
            'fecha_iso': fecha_dia.isoformat(),
            'es_hoy': fecha_dia == timezone.localdate(),
            'es_finde': fecha_dia.weekday() >= 5,
            'dow': fecha_dia.weekday(),
        })

    return filas, dias_cabecera, dias_en_mes


def _construir_semana(reservas, semana_inicio, hoy):
    dias = []
    for i in range(7):
        fecha_dia = semana_inicio + timedelta(days=i)
        eventos_dia = []
        for reserva in reservas:
            if reserva.fecha_inicio <= fecha_dia <= reserva.fecha_fin:
                eventos_dia.append(_evento_desde_reserva(reserva, fecha_dia))
        dias.append({
            'numero': fecha_dia.day,
            'nombre': DIAS_SEMANA_LARGO[i],
            'nombre_corto': DIAS_SEMANA[i],
            'fecha_iso': fecha_dia.isoformat(),
            'es_hoy': fecha_dia == hoy,
            'es_finde': i >= 5,
            'es_pasado': fecha_dia < hoy,
            'en_mes': True,
            'eventos': eventos_dia,
            'total_eventos': len(eventos_dia),
            'dow': i,
        })
    return dias


def index(request):
    hoy = timezone.localdate()

    try:
        anio = int(request.GET.get('anio', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))
        date(anio, mes, 1)
    except (TypeError, ValueError):
        anio, mes = hoy.year, hoy.month

    filtro_estado = request.GET.get('estado', '')
    filtro_vehiculo = request.GET.get('vehiculo', '')
    filtro_cliente = request.GET.get('cliente', '')
    vista = request.GET.get('vista', 'mes')
    if vista not in ('mes', 'gantt', 'semana'):
        vista = 'mes'

    primer_dia, ultimo_dia = _rango_mes(anio, mes)

    semana_ref = primer_dia
    if anio == hoy.year and mes == hoy.month:
        semana_ref = date(anio, mes, min(hoy.day, ultimo_dia.day))
    try:
        dia_param = request.GET.get('dia')
        if dia_param:
            semana_ref = date(anio, mes, int(dia_param))
    except (TypeError, ValueError):
        pass
    semana_inicio = _semana_lunes(semana_ref)
    semana_fin = semana_inicio + timedelta(days=6)

    consulta_inicio = min(primer_dia, semana_inicio) if vista == 'semana' else primer_dia
    consulta_fin = max(ultimo_dia, semana_fin) if vista == 'semana' else ultimo_dia

    reservas_qs = (
        Reserva.objects.filter(
            fecha_inicio__lte=consulta_fin,
            fecha_fin__gte=consulta_inicio,
        )
        .exclude(estado=Reserva.Estado.CANCELADA)
        .select_related('cliente', 'vehiculo')
        .order_by('fecha_inicio', 'hora_entrega')
    )

    if filtro_estado:
        reservas_qs = reservas_qs.filter(estado=filtro_estado)
    if filtro_vehiculo:
        reservas_qs = reservas_qs.filter(vehiculo_id=filtro_vehiculo)
    if filtro_cliente:
        reservas_qs = reservas_qs.filter(cliente_id=filtro_cliente)

    reservas = list(reservas_qs)

    eventos_por_dia = {}
    entregas_mes = 0
    devoluciones_mes = 0
    sin_pagar = 0
    entregas_hoy = 0
    devoluciones_hoy = 0

    for reserva in reservas:
        if primer_dia <= reserva.fecha_inicio <= ultimo_dia:
            entregas_mes += 1
        if primer_dia <= reserva.fecha_fin <= ultimo_dia:
            devoluciones_mes += 1
        if reserva.estado_pago != 'pagado':
            sin_pagar += 1
        if reserva.fecha_inicio == hoy:
            entregas_hoy += 1
        if reserva.fecha_fin == hoy:
            devoluciones_hoy += 1

        dia_actual = max(reserva.fecha_inicio, consulta_inicio)
        dia_final = min(reserva.fecha_fin, consulta_fin)
        while dia_actual <= dia_final:
            eventos_por_dia.setdefault(dia_actual, []).append(
                _evento_desde_reserva(reserva, dia_actual)
            )
            dia_actual += timedelta(days=1)

    hoy_dow = hoy.weekday()
    cal = calendar.Calendar(firstweekday=0)
    semanas = []

    for semana in cal.monthdayscalendar(anio, mes):
        dias = []
        for idx, dia in enumerate(semana):
            if dia == 0:
                dias.append({'numero': None, 'en_mes': False, 'eventos': []})
            else:
                fecha_dia = date(anio, mes, dia)
                eventos_dia = eventos_por_dia.get(fecha_dia, [])
                dias.append({
                    'numero': dia,
                    'en_mes': True,
                    'es_hoy': fecha_dia == hoy,
                    'es_finde': idx >= 5,
                    'es_pasado': fecha_dia < hoy,
                    'es_col_hoy': idx == hoy_dow and fecha_dia.month == hoy.month and anio == hoy.year,
                    'dow': idx,
                    'eventos': eventos_dia,
                    'fecha_iso': fecha_dia.isoformat(),
                    'total_eventos': len(eventos_dia),
                })
        semanas.append(dias)

    eventos_json = {
        fecha_dia.isoformat(): eventos
        for fecha_dia, eventos in eventos_por_dia.items()
    }

    vehiculos = Vehiculo.objects.filter(activo=True).order_by('marca', 'modelo')
    if filtro_vehiculo:
        vehiculos_gantt = vehiculos.filter(pk=filtro_vehiculo)
    else:
        vehiculos_gantt = vehiculos

    gantt_filas, gantt_dias, dias_en_mes = _construir_gantt(
        reservas, primer_dia, ultimo_dia, vehiculos_gantt,
    )

    dias_semana = _construir_semana(reservas, semana_inicio, hoy)

    semana_prev = semana_inicio - timedelta(days=7)
    semana_next = semana_inicio + timedelta(days=7)

    clientes_ids = {r.cliente_id for r in reservas}
    clientes_filtro = Cliente.objects.filter(pk__in=clientes_ids).order_by('nombre', 'apellido')

    anio_prev, mes_prev = _mes_anterior(anio, mes)
    anio_next, mes_next = _mes_siguiente(anio, mes)
    total_mes = len(reservas)
    query_extra = _query_string(filtro_estado, filtro_vehiculo, filtro_cliente, vista)
    query_filtros = _query_string(filtro_estado, filtro_vehiculo, filtro_cliente, '')

    anios_opciones = list(range(hoy.year - 2, hoy.year + 3))
    meses_opciones = list(enumerate(MESES[1:], start=1))

    return render(request, 'calendario/calendario.html', {
        'page_title': 'Calendario',
        'page_subtitle': f'{MESES[mes]} {anio} · {total_mes} reserva{"s" if total_mes != 1 else ""}',
        'anio': anio,
        'mes': mes,
        'mes_nombre': MESES[mes],
        'semanas': semanas,
        'dias_semana': DIAS_SEMANA,
        'anio_prev': anio_prev,
        'mes_prev': mes_prev,
        'anio_next': anio_next,
        'mes_next': mes_next,
        'hoy_anio': hoy.year,
        'hoy_mes': hoy.month,
        'hoy_dow': hoy_dow,
        'eventos_json': eventos_json,
        'entregas_mes': entregas_mes,
        'devoluciones_mes': devoluciones_mes,
        'entregas_hoy': entregas_hoy,
        'devoluciones_hoy': devoluciones_hoy,
        'sin_pagar': sin_pagar,
        'total_mes': total_mes,
        'filtro_estado': filtro_estado,
        'filtro_vehiculo': filtro_vehiculo,
        'filtro_cliente': filtro_cliente,
        'estados': Reserva.Estado.choices,
        'vehiculos': vehiculos,
        'clientes_filtro': clientes_filtro,
        'query_extra': query_extra,
        'query_filtros': query_filtros,
        'vista': vista,
        'gantt_filas': gantt_filas,
        'gantt_dias': gantt_dias,
        'dias_en_mes': dias_en_mes,
        'dias_semana_vista': dias_semana,
        'semana_inicio': semana_inicio,
        'semana_fin': semana_fin,
        'semana_prev': semana_prev,
        'semana_next': semana_next,
        'anios_opciones': anios_opciones,
        'meses_opciones': meses_opciones,
    })
