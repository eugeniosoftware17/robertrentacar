from calendar import month_abbr
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from apps.pagos.models import Pago
from apps.reservas.models import Reserva
from apps.reservas.services import actualizar_estados_reservas
from apps.vehiculos.models import Vehiculo


def _neto_pagos(queryset):
    cobros = queryset.exclude(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t'] or Decimal('0')
    reembolsos = queryset.filter(tipo=Pago.Tipo.REEMBOLSO).aggregate(t=Sum('monto'))['t'] or Decimal('0')
    return cobros - reembolsos


def dashboard(request):
    actualizar_estados_reservas()

    hoy = timezone.localdate()
    manana = hoy + timedelta(days=1)
    inicio_mes = hoy.replace(day=1)

    vehiculos_activos = Vehiculo.objects.filter(activo=True)
    total_vehiculos = vehiculos_activos.count()
    vehiculos_disponibles = vehiculos_activos.filter(estado=Vehiculo.Estado.DISPONIBLE).count()

    reservas_hoy = Reserva.objects.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy,
    ).exclude(estado=Reserva.Estado.CANCELADA).count()

    reservas_confirmadas_hoy = Reserva.objects.filter(
        fecha_inicio=hoy,
        estado=Reserva.Estado.CONFIRMADA,
    ).count()

    entregas_hoy = Reserva.objects.filter(
        fecha_inicio=hoy,
    ).exclude(estado=Reserva.Estado.CANCELADA).count()

    devoluciones_hoy = Reserva.objects.filter(
        fecha_fin=hoy,
    ).exclude(estado=Reserva.Estado.CANCELADA).count()

    entregas_manana = Reserva.objects.filter(
        fecha_inicio=manana,
    ).exclude(estado=Reserva.Estado.CANCELADA).count()

    devoluciones_manana = Reserva.objects.filter(
        fecha_fin=manana,
    ).exclude(estado=Reserva.Estado.CANCELADA).count()

    movimientos_total = entregas_hoy + devoluciones_hoy + entregas_manana + devoluciones_manana

    reservas_mes = Reserva.objects.filter(
        fecha_inicio__gte=inicio_mes,
        fecha_inicio__lte=hoy,
    ).exclude(estado=Reserva.Estado.CANCELADA)

    facturado_mes = reservas_mes.aggregate(total=Sum('precio_total'))['total'] or Decimal('0.00')

    cobrado_reservas_mes = Decimal('0.00')
    for r in reservas_mes:
        cobrado_reservas_mes += r.total_pagado
    saldo_pendiente_mes = facturado_mes - cobrado_reservas_mes

    caja_mes = _neto_pagos(Pago.objects.filter(
        fecha__date__gte=inicio_mes,
        fecha__date__lte=hoy,
    ))

    inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    fin_mes_anterior = inicio_mes - timedelta(days=1)

    caja_mes_anterior = _neto_pagos(Pago.objects.filter(
        fecha__date__gte=inicio_mes_anterior,
        fecha__date__lte=fin_mes_anterior,
    ))

    if caja_mes_anterior > 0:
        variacion_caja = ((caja_mes - caja_mes_anterior) / caja_mes_anterior) * 100
    else:
        variacion_caja = Decimal('0.00')

    proximos_movimientos = []
    movimientos_qs = Reserva.objects.select_related('cliente', 'vehiculo').exclude(
        estado=Reserva.Estado.CANCELADA,
    ).filter(
        Q(fecha_inicio__in=[hoy, manana]) | Q(fecha_fin__in=[hoy, manana])
    ).order_by('fecha_inicio', 'hora_entrega')[:6]

    for reserva in movimientos_qs:
        if reserva.fecha_inicio in (hoy, manana):
            tipo = 'Entrega'
            fecha_ref = reserva.fecha_inicio
            hora = reserva.hora_entrega
            lugar = reserva.lugar_entrega
        else:
            tipo = 'Devolución'
            fecha_ref = reserva.fecha_fin
            hora = reserva.hora_devolucion
            lugar = reserva.lugar_devolucion

        hora_texto = hora.strftime('%I:%M %p').lstrip('0').lower()
        if fecha_ref == hoy:
            fecha_texto = f'Hoy, {hora_texto}'
        else:
            fecha_texto = f'Mañana, {hora_texto}'

        proximos_movimientos.append({
            'vehiculo': reserva.vehiculo.nombre_corto,
            'tipo': tipo,
            'cliente': reserva.cliente.nombre_completo,
            'fecha_texto': fecha_texto,
            'lugar': lugar,
            'reserva_id': reserva.pk,
            'url_entrega': tipo == 'Entrega' and reserva.puede_registrar_entrega and not reserva.entrega_registrada,
            'url_devolucion': tipo == 'Devolución' and reserva.puede_registrar_devolucion and reserva.entrega_registrada,
        })

    top_vehiculos = (
        Reserva.objects.filter(
            fecha_inicio__gte=inicio_mes,
            fecha_inicio__lte=hoy,
        )
        .exclude(estado=Reserva.Estado.CANCELADA)
        .values('vehiculo__marca', 'vehiculo__modelo', 'vehiculo__pk')
        .annotate(
            total_reservas=Count('id'),
            ingresos=Sum('precio_total'),
        )
        .order_by('-total_reservas')[:3]
    )

    alertas = []
    for vehiculo in vehiculos_activos.filter(seguro_vence__isnull=False, seguro_vence__lt=hoy):
        dias_vencido = (hoy - vehiculo.seguro_vence).days
        alertas.append({
            'nombre': vehiculo.nombre_corto,
            'detalle': f'Seguro vencido hace {dias_vencido} día{"s" if dias_vencido != 1 else ""}',
            'tipo': 'Urgente',
            'clase': 'rojo',
            'icono': '📄',
            'fondo': '#f9e9e9',
            'prioridad': 0,
        })

    for vehiculo in vehiculos_activos.filter(estado=Vehiculo.Estado.MANTENIMIENTO):
        alertas.append({
            'nombre': vehiculo.nombre_corto,
            'detalle': 'En mantenimiento',
            'tipo': 'Urgente',
            'clase': 'rojo',
            'icono': '⚠️',
            'fondo': '#f9e9e9',
            'prioridad': 0,
        })

    for vehiculo in vehiculos_activos.filter(
        seguro_vence__isnull=False,
        seguro_vence__lte=hoy + timedelta(days=30),
        seguro_vence__gte=hoy,
    ):
        alertas.append({
            'nombre': vehiculo.nombre_corto,
            'detalle': f'Seguro vence el {vehiculo.seguro_vence.strftime("%d de %B")}',
            'tipo': 'Aviso',
            'clase': 'azul',
            'icono': '📄',
            'fondo': '#d9eeee',
            'prioridad': 1,
        })

    for vehiculo in vehiculos_activos.filter(
        prox_mantenimiento__isnull=False,
        prox_mantenimiento__lte=hoy + timedelta(days=7),
        prox_mantenimiento__gte=hoy,
    ).exclude(estado=Vehiculo.Estado.MANTENIMIENTO):
        dias = (vehiculo.prox_mantenimiento - hoy).days
        alertas.append({
            'nombre': vehiculo.nombre_corto,
            'detalle': f'Revisión general en {dias} días',
            'tipo': 'Próximo',
            'clase': 'amarillo',
            'icono': '🔧',
            'fondo': '#f8f0de',
            'prioridad': 2,
        })

    alertas.sort(key=lambda a: a['prioridad'])

    hace_6_meses = hoy.replace(day=1) - timedelta(days=150)
    pagos_agrupados = (
        Pago.objects.filter(fecha__date__gte=hace_6_meses)
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(
            cobros=Sum('monto', filter=~Q(tipo=Pago.Tipo.REEMBOLSO)),
            reembolsos=Sum('monto', filter=Q(tipo=Pago.Tipo.REEMBOLSO)),
        )
        .order_by('mes')
    )

    meses_cobrado = {}
    for item in pagos_agrupados:
        if item['mes']:
            neto = (item['cobros'] or Decimal('0')) - (item['reembolsos'] or Decimal('0'))
            meses_cobrado[(item['mes'].year, item['mes'].month)] = float(neto)

    grafica_datos = []
    for i in range(5, -1, -1):
        fecha = (hoy.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        mes_num = fecha.month
        total = meses_cobrado.get((fecha.year, mes_num), 0)
        grafica_datos.append({
            'mes': month_abbr[mes_num],
            'valor': round(total / 1000, 1),
            'valor_real': total,
        })

    return render(request, 'dashboard.html', {
        'page_title': 'Dashboard',
        'page_subtitle': 'Resumen de la operación en tiempo real',
        'vehiculos_disponibles': vehiculos_disponibles,
        'total_vehiculos': total_vehiculos,
        'reservas_hoy': reservas_hoy,
        'reservas_confirmadas_hoy': reservas_confirmadas_hoy,
        'movimientos_total': movimientos_total,
        'entregas_hoy': entregas_hoy,
        'devoluciones_hoy': devoluciones_hoy,
        'entregas_manana': entregas_manana,
        'devoluciones_manana': devoluciones_manana,
        'facturado_mes': facturado_mes,
        'cobrado_mes': cobrado_reservas_mes,
        'caja_mes': caja_mes,
        'saldo_pendiente_mes': saldo_pendiente_mes,
        'variacion_caja': variacion_caja,
        'proximos_movimientos': proximos_movimientos,
        'top_vehiculos': top_vehiculos,
        'alertas': alertas[:6],
        'grafica_datos': grafica_datos,
    })
