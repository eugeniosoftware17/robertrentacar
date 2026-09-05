from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import paginar_queryset
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

from .forms import PagoForm
from .models import Pago


def _reservas_financiero():
    data = {}
    for r in Reserva.objects.exclude(estado=Reserva.Estado.CANCELADA).select_related('cliente', 'vehiculo'):
        data[str(r.pk)] = {
            'cliente': r.cliente.nombre_completo,
            'vehiculo': r.vehiculo.nombre_corto,
            'placa': r.vehiculo.placa,
            'dias': r.dias,
            'precio_total': float(r.precio_total),
            'total_pagado': float(r.total_pagado),
            'saldo_pendiente': float(r.saldo_pendiente),
            'estado_pago': r.estado_pago,
            'estado_pago_label': r.estado_pago_label,
        }
    return data


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    pagos = Pago.objects.select_related('reserva__cliente', 'reserva__vehiculo')

    if busqueda:
        pagos = pagos.filter(
            Q(reserva__cliente__nombre__icontains=busqueda)
            | Q(reserva__cliente__apellido__icontains=busqueda)
            | Q(reserva__vehiculo__placa__icontains=busqueda)
            | Q(referencia__icontains=busqueda)
        )

    cobros = pagos.exclude(tipo=Pago.Tipo.REEMBOLSO).aggregate(total=Sum('monto'))['total'] or 0
    reembolsos = pagos.filter(tipo=Pago.Tipo.REEMBOLSO).aggregate(total=Sum('monto'))['total'] or 0
    total_neto = cobros - reembolsos

    page_obj = paginar_queryset(request, pagos)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    return render(request, 'pagos/lista.html', {
        'page_title': 'Pagos',
        'page_subtitle': 'Cobros y depósitos de reservas',
        'pagos': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'total_cobrado': total_neto,
        'total': pagos.count(),
    })


def crear(request):
    reservas_info = _reservas_financiero()
    reserva_sel = None

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            messages.success(request, f'Pago de USD$ {pago.monto:,.2f} registrado.')
            return redirect('pagos:lista')
    else:
        initial = {}
        reserva_id = request.GET.get('reserva')
        if reserva_id:
            initial['reserva'] = reserva_id
            try:
                reserva = Reserva.objects.get(pk=reserva_id)
                reserva_sel = reserva
                saldo = reserva.saldo_pendiente
                if saldo > 0:
                    initial['tipo'] = Pago.Tipo.DEPOSITO if reserva.total_pagado == 0 else Pago.Tipo.PARCIAL
            except Reserva.DoesNotExist:
                pass
        form = PagoForm(initial=initial)

    return render(request, 'pagos/formulario.html', {
        'page_title': 'Registrar pago',
        'page_subtitle': 'Nuevo cobro o depósito',
        'form': form,
        'accion': 'crear',
        'reservas_info': reservas_info,
        'reserva_sel': reserva_sel,
    })


def eliminar(request, pk):
    pago = get_object_or_404(Pago, pk=pk)

    if request.method == 'POST':
        monto = pago.monto
        pago.delete()
        messages.success(request, f'Pago de USD$ {monto:,.2f} eliminado.')
        return redirect('pagos:lista')

    return render(request, 'pagos/confirmar_eliminar.html', {
        'page_title': 'Eliminar pago',
        'page_subtitle': str(pago),
        'pago': pago,
    })
