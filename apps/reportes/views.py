from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.pagos.models import Pago
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

from .exports import respuesta_csv


def _neto_pagos(queryset):
    cobros = queryset.exclude(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t'] or Decimal('0')
    reembolsos = queryset.filter(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t'] or Decimal('0')
    return cobros - reembolsos


def index(request):
    return render(request, 'reportes/index.html', {
        'page_title': 'Reportes',
        'page_subtitle': 'Análisis de la operación',
    })


def ingresos(request):
    hoy = timezone.localdate()
    desde = request.GET.get('desde') or (hoy.replace(day=1)).isoformat()
    hasta = request.GET.get('hasta') or hoy.isoformat()

    reservas = Reserva.objects.filter(
        fecha_inicio__gte=desde,
        fecha_inicio__lte=hasta,
    ).exclude(estado=Reserva.Estado.CANCELADA).select_related('cliente', 'vehiculo')

    if request.GET.get('exportar') == 'csv':
        filas = []
        for r in reservas.order_by('fecha_inicio'):
            filas.append([
                r.pk,
                r.cliente.nombre_completo,
                r.vehiculo.placa,
                r.fecha_inicio.isoformat(),
                r.fecha_fin.isoformat(),
                r.get_estado_display(),
                float(r.precio_total),
                float(r.total_pagado),
                float(r.saldo_pendiente),
            ])
        return respuesta_csv(
            f'ingresos_{desde}_{hasta}.csv',
            filas,
            ['Reserva', 'Cliente', 'Placa', 'Inicio', 'Fin', 'Estado', 'Facturado', 'Cobrado', 'Saldo'],
        )

    totales = reservas.aggregate(
        facturado=Sum('precio_total'),
        reservas=Count('id'),
    )
    facturado_total = totales['facturado'] or Decimal('0.00')

    cobrado_total = Decimal('0.00')
    for r in reservas:
        cobrado_total += r.total_pagado

    por_estado = []
    for value, label in Reserva.Estado.choices:
        subset = reservas.filter(estado=value)
        agg = subset.aggregate(total=Sum('precio_total'), cantidad=Count('id'))
        if not agg['cantidad']:
            continue
        cobrado_estado = Decimal('0.00')
        for r in subset:
            cobrado_estado += r.total_pagado
        por_estado.append({
            'estado': label,
            'cantidad': agg['cantidad'],
            'facturado': agg['total'] or Decimal('0.00'),
            'cobrado': cobrado_estado,
            'saldo': (agg['total'] or Decimal('0.00')) - cobrado_estado,
        })

    pagos_periodo = Pago.objects.filter(
        fecha__date__gte=desde,
        fecha__date__lte=hasta,
    )
    caja_periodo = _neto_pagos(pagos_periodo)

    return render(request, 'reportes/ingresos.html', {
        'page_title': 'Reporte de ingresos',
        'page_subtitle': f'Del {desde} al {hasta}',
        'desde': desde,
        'hasta': hasta,
        'facturado_total': facturado_total,
        'cobrado_total': cobrado_total,
        'saldo_pendiente': facturado_total - cobrado_total,
        'caja_periodo': caja_periodo,
        'total_reservas': totales['reservas'] or 0,
        'por_estado': por_estado,
    })


def ocupacion(request):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    if hoy.month == 12:
        fin_mes = hoy.replace(day=31)
    else:
        fin_mes = (hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1))

    vehiculos = Vehiculo.objects.filter(activo=True)
    total_vehiculos = vehiculos.count()
    dias_mes = (fin_mes - inicio_mes).days + 1

    filas = []
    for vehiculo in vehiculos:
        reservas = Reserva.objects.filter(
            vehiculo=vehiculo,
            fecha_inicio__lte=fin_mes,
            fecha_fin__gte=inicio_mes,
        ).exclude(estado=Reserva.Estado.CANCELADA)

        dias_ocupados = 0
        for reserva in reservas:
            inicio = max(reserva.fecha_inicio, inicio_mes)
            fin = min(reserva.fecha_fin, fin_mes)
            dias_ocupados += (fin - inicio).days + 1

        ocupacion_pct = round((dias_ocupados / dias_mes) * 100, 1) if dias_mes else 0
        filas.append({
            'vehiculo': vehiculo,
            'dias_ocupados': dias_ocupados,
            'ocupacion_pct': ocupacion_pct,
            'reservas': reservas.count(),
        })

    filas.sort(key=lambda x: x['ocupacion_pct'], reverse=True)

    if request.GET.get('exportar') == 'csv':
        csv_filas = [
            [f['vehiculo'].nombre_corto, f['vehiculo'].placa, f['dias_ocupados'], f['ocupacion_pct'], f['reservas']]
            for f in filas
        ]
        return respuesta_csv(
            f'ocupacion_{inicio_mes.strftime("%Y-%m")}.csv',
            csv_filas,
            ['Vehículo', 'Placa', 'Días ocupados', 'Ocupación %', 'Reservas'],
        )

    return render(request, 'reportes/ocupacion.html', {
        'page_title': 'Ocupación de flota',
        'page_subtitle': f'{inicio_mes.strftime("%B %Y")}',
        'filas': filas,
        'total_vehiculos': total_vehiculos,
        'dias_mes': dias_mes,
    })
