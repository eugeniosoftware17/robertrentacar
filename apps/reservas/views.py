import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.configuracion.models import ConfiguracionEmpresa
from apps.core.utils import paginar_queryset
from apps.sitio.models import ConfiguracionSitio
from apps.vehiculos.models import Vehiculo

from .forms import ConductorAdicionalForm, DevolucionForm, EntregaForm, ReservaForm
from .models import ConductorAdicional, Reserva
from .pdf import render_pdf
from .services import actualizar_estado_vehiculo

logger = logging.getLogger(__name__)


def _guardar_conductor_adicional(reserva, conductor_form):
    conductor = conductor_form.save(commit=False)
    if conductor.tiene_datos():
        conductor.reserva = reserva
        conductor.save()
    else:
        ConductorAdicional.objects.filter(reserva=reserva).delete()


def _tarifas_vehiculos():
    return {
        str(v.pk): float(v.tarifa_diaria)
        for v in Vehiculo.objects.filter(activo=True)
    }


def _ocupacion_por_vehiculo(excluir_reserva_id=None):
    """Fechas ocupadas por vehículo (reservas activas, no canceladas)."""
    reservas = Reserva.objects.exclude(
        estado=Reserva.Estado.CANCELADA,
    ).select_related('cliente')

    if excluir_reserva_id:
        reservas = reservas.exclude(pk=excluir_reserva_id)

    data = {}
    for reserva in reservas:
        vid = str(reserva.vehiculo_id)
        if vid not in data:
            data[vid] = {'dias': [], 'bloques': []}

        data[vid]['bloques'].append({
            'inicio': reserva.fecha_inicio.isoformat(),
            'fin': reserva.fecha_fin.isoformat(),
            'cliente': reserva.cliente.nombre_completo,
            'id': reserva.pk,
        })

        dia = reserva.fecha_inicio
        while dia <= reserva.fecha_fin:
            iso = dia.isoformat()
            if iso not in data[vid]['dias']:
                data[vid]['dias'].append(iso)
            dia += timedelta(days=1)

    return data


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    origen = request.GET.get('origen', '')
    reservas = Reserva.objects.select_related('cliente', 'vehiculo')

    if busqueda:
        reservas = reservas.filter(
            Q(cliente__nombre__icontains=busqueda)
            | Q(cliente__apellido__icontains=busqueda)
            | Q(vehiculo__marca__icontains=busqueda)
            | Q(vehiculo__modelo__icontains=busqueda)
            | Q(vehiculo__placa__icontains=busqueda)
        )

    if estado:
        reservas = reservas.filter(estado=estado)

    if origen in (Reserva.Origen.WEB, Reserva.Origen.PANEL):
        reservas = reservas.filter(origen=origen)

    page_obj = paginar_queryset(request, reservas)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    return render(request, 'reservas/lista.html', {
        'page_title': 'Reservas',
        'page_subtitle': 'Gestión de reservas y alquileres',
        'reservas': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'estado_filtro': estado,
        'origen_filtro': origen,
        'estados': Reserva.Estado.choices,
        'total': reservas.count(),
    })


ESTADOS_CONTRATO = (
    Reserva.Estado.CONFIRMADA,
    Reserva.Estado.ACTIVA,
    Reserva.Estado.COMPLETADA,
)


def lista_contratos(request):
    """Reservas formalizadas (confirmadas o en curso) para ver/imprimir contrato."""
    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    reservas = Reserva.objects.select_related('cliente', 'vehiculo').filter(
        estado__in=ESTADOS_CONTRATO,
    )

    if busqueda:
        reservas = reservas.filter(
            Q(cliente__nombre__icontains=busqueda)
            | Q(cliente__apellido__icontains=busqueda)
            | Q(vehiculo__marca__icontains=busqueda)
            | Q(vehiculo__modelo__icontains=busqueda)
            | Q(vehiculo__placa__icontains=busqueda)
        )

    if estado and estado in ESTADOS_CONTRATO:
        reservas = reservas.filter(estado=estado)

    page_obj = paginar_queryset(request, reservas)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    estados_filtro = [
        (value, label)
        for value, label in Reserva.Estado.choices
        if value in ESTADOS_CONTRATO
    ]

    return render(request, 'reservas/contratos.html', {
        'page_title': 'Contratos',
        'page_subtitle': 'Documentos de alquiler formalizados',
        'reservas': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'estado_filtro': estado,
        'estados': estados_filtro,
        'total': reservas.count(),
    })


def crear(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        conductor_form = ConductorAdicionalForm(request.POST, prefix='conductor')
        if form.is_valid() and conductor_form.is_valid():
            reserva = form.save()
            _guardar_conductor_adicional(reserva, conductor_form)
            messages.success(request, f'Reserva #{reserva.pk} creada correctamente.')
            return redirect('reservas:lista')
    else:
        initial = {}
        fecha_inicio = request.GET.get('fecha_inicio')
        if fecha_inicio:
            initial['fecha_inicio'] = fecha_inicio
            initial['fecha_fin'] = fecha_inicio
        form = ReservaForm(initial=initial)
        conductor_form = ConductorAdicionalForm(prefix='conductor')

    return render(request, 'reservas/formulario.html', {
        'page_title': 'Nueva reserva',
        'page_subtitle': 'Registrar una nueva reserva',
        'form': form,
        'conductor_form': conductor_form,
        'accion': 'crear',
        'tarifas_json': _tarifas_vehiculos(),
        'ocupacion_json': _ocupacion_por_vehiculo(),
    })


def _notificar_confirmacion_reserva(reserva):
    logger.info(f'Intentando notificar confirmación reserva #{reserva.pk}, email cliente: "{reserva.cliente.email}"')
    if not reserva.cliente.email:
        return
    mensaje = (
        f'Estimado/a {reserva.cliente.nombre_completo},\n\n'
        f'Su reserva ha sido confirmada. Aquí están los detalles:\n\n'
        f'Vehículo: {reserva.vehiculo.nombre_corto}\n'
        f'Fechas: {reserva.fecha_inicio.strftime("%d/%m/%Y")} — {reserva.fecha_fin.strftime("%d/%m/%Y")}\n'
        f'Días: {reserva.dias}\n'
        f'Total: USD$ {reserva.precio_total}\n'
        f'Depósito pagado: USD$ {reserva.total_pagado}\n'
        f'Saldo pendiente: USD$ {reserva.saldo_pendiente}\n\n'
        f'Lugar de entrega: {reserva.lugar_entrega or "Por confirmar"}\n\n'
        f'Para cualquier consulta puede contactarnos por WhatsApp.\n\n'
        f'Gracias por elegir ROB-REI Rent A Car.\n'
    )
    try:
        send_mail(
            subject=f'Reserva confirmada — {reserva.vehiculo.nombre_corto}',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.cliente.email],
        )
        logger.info(f'Email confirmación enviado a {reserva.cliente.email} reserva #{reserva.pk}')
    except Exception as e:
        logger.error(f'Error enviando email confirmación reserva #{reserva.pk}: {e}')


def _notificar_entrega(reserva):
    logger.info(f'Intentando notificar entrega reserva #{reserva.pk}, email cliente: "{reserva.cliente.email}"')
    if not reserva.cliente.email:
        return
    mensaje = (
        f'Estimado/a {reserva.cliente.nombre_completo},\n\n'
        f'Le confirmamos que el vehículo ha sido entregado. Aquí están los detalles de su alquiler:\n\n'
        f'Vehículo: {reserva.vehiculo.nombre_corto}\n'
        f'Fechas: {reserva.fecha_inicio.strftime("%d/%m/%Y")} — {reserva.fecha_fin.strftime("%d/%m/%Y")}\n'
        f'Días: {reserva.dias}\n'
        f'Total: USD$ {reserva.precio_total}\n'
        f'Pagado: USD$ {reserva.total_pagado}\n'
        f'Saldo pendiente: USD$ {reserva.saldo_pendiente}\n\n'
        f'Recuerde que el pago restante se realiza al devolver el vehículo.\n\n'
        f'Para cualquier consulta puede contactarnos por WhatsApp.\n\n'
        f'Gracias por elegir ROB-REI Rent A Car.\n'
    )
    try:
        send_mail(
            subject=f'Entrega de vehículo — {reserva.vehiculo.nombre_corto}',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.cliente.email],
        )
        logger.info(f'Email entrega enviado a {reserva.cliente.email} reserva #{reserva.pk}')
    except Exception as e:
        logger.error(f'Error enviando email entrega reserva #{reserva.pk}: {e}')


def _notificar_devolucion(reserva):
    logger.info(f'Intentando notificar devolución reserva #{reserva.pk}, email cliente: "{reserva.cliente.email}"')
    if not reserva.cliente.email:
        return
    mensaje = (
        f'Estimado/a {reserva.cliente.nombre_completo},\n\n'
        f'Esperamos que haya disfrutado su experiencia con ROB-REI Rent A Car.\n\n'
        f'Su alquiler ha sido completado exitosamente:\n\n'
        f'Vehículo: {reserva.vehiculo.nombre_corto}\n'
        f'Fechas: {reserva.fecha_inicio.strftime("%d/%m/%Y")} — {reserva.fecha_fin.strftime("%d/%m/%Y")}\n'
        f'Total pagado: USD$ {reserva.precio_total}\n\n'
        f'Nos encantaría conocer su opinión. Si tuvo una buena experiencia, \n'
        f'le agradecemos mucho que nos deje una reseña en Google:\n\n'
        f'👉 https://share.google/Rgv0l703tNeGMne0P\n\n'
        f'Su opinión nos ayuda a seguir mejorando y a que otros viajeros \n'
        f'puedan encontrarnos.\n\n'
        f'¡Gracias y esperamos verle pronto!\n\n'
        f'ROB-REI Rent A Car\n'
    )
    try:
        send_mail(
            subject='¡Gracias por alquilar con nosotros! — ROB-REI Rent A Car',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.cliente.email],
        )
        logger.info(f'Email devolución enviado a {reserva.cliente.email} reserva #{reserva.pk}')
    except Exception as e:
        logger.error(f'Error enviando email devolución reserva #{reserva.pk}: {e}')


def editar(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente', 'vehiculo', 'conductor_adicional'),
        pk=pk,
    )
    conductor_instance = getattr(reserva, 'conductor_adicional', None)

    if request.method == 'POST':
        if 'marcar_contactado' in request.POST:
            reserva.requiere_contacto_web = False
            reserva.save(update_fields=['requiere_contacto_web'])
            messages.success(request, 'Reserva marcada como contactada.')
            return redirect('reservas:editar', pk=pk)
        estado_anterior = reserva.estado
        form = ReservaForm(request.POST, instance=reserva)
        conductor_form = ConductorAdicionalForm(
            request.POST, instance=conductor_instance, prefix='conductor',
        )
        if form.is_valid() and conductor_form.is_valid():
            reserva = form.save()
            _guardar_conductor_adicional(reserva, conductor_form)
            actualizar_estado_vehiculo(reserva.vehiculo)
            if estado_anterior != Reserva.Estado.CONFIRMADA and reserva.estado == Reserva.Estado.CONFIRMADA:
                _notificar_confirmacion_reserva(reserva)
            messages.success(request, f'Reserva #{reserva.pk} actualizada.')
            return redirect('reservas:lista')
    else:
        form = ReservaForm(instance=reserva)
        conductor_form = ConductorAdicionalForm(instance=conductor_instance, prefix='conductor')

    return render(request, 'reservas/formulario.html', {
        'page_title': 'Editar reserva',
        'page_subtitle': f'Reserva #{reserva.pk}',
        'form': form,
        'conductor_form': conductor_form,
        'accion': 'editar',
        'reserva': reserva,
        'tarifas_json': _tarifas_vehiculos(),
        'ocupacion_json': _ocupacion_por_vehiculo(excluir_reserva_id=reserva.pk),
    })


def cancelar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if reserva.estado == Reserva.Estado.CANCELADA:
        messages.info(request, f'La reserva #{reserva.pk} ya está cancelada.')
        return redirect('reservas:lista')

    if request.method == 'POST':
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save(update_fields=['estado'])
        actualizar_estado_vehiculo(reserva.vehiculo)
        messages.success(request, f'Reserva #{reserva.pk} cancelada.')
        return redirect('reservas:lista')

    return render(request, 'reservas/confirmar_cancelar.html', {
        'page_title': 'Cancelar reserva',
        'page_subtitle': f'Reserva #{reserva.pk}',
        'reserva': reserva,
    })


def eliminar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        vehiculo = reserva.vehiculo
        reserva_id = reserva.pk
        try:
            reserva.delete()
            actualizar_estado_vehiculo(vehiculo)
            messages.success(request, f'Reserva #{reserva_id} eliminada.')
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar: tiene pagos registrados. Cancela la reserva en su lugar.',
            )
        return redirect('reservas:lista')

    return render(request, 'reservas/confirmar_eliminar.html', {
        'page_title': 'Eliminar reserva',
        'page_subtitle': f'Reserva #{reserva.pk}',
        'reserva': reserva,
    })


def contrato(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente', 'vehiculo', 'conductor_adicional'),
        pk=pk,
    )
    empresa = ConfiguracionEmpresa.obtener()
    sitio = ConfiguracionSitio.obtener()

    return render(request, 'reservas/contrato.html', {
        'page_title': f'Contrato #{reserva.pk}',
        'page_subtitle': reserva.cliente.nombre_completo,
        'reserva': reserva,
        'empresa': empresa,
        'sitio': sitio,
    })


def contrato_pdf(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente', 'vehiculo', 'conductor_adicional'),
        pk=pk,
    )
    return render_pdf('reservas/contrato_pdf.html', {
        'reserva': reserva,
        'empresa': ConfiguracionEmpresa.obtener(),
        'sitio': ConfiguracionSitio.obtener(),
    }, f'contrato-{reserva.pk}.pdf')


def entrega(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente', 'vehiculo'),
        pk=pk,
    )

    if not reserva.puede_registrar_entrega:
        messages.warning(request, 'Esta reserva no está lista para registrar entrega.')
        return redirect('reservas:editar', pk=pk)

    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES, instance=reserva)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.entrega_registrada = True
            if reserva.estado in (Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA):
                reserva.estado = Reserva.Estado.ACTIVA
            reserva.save()
            reserva.vehiculo.kilometraje = reserva.km_entrega
            reserva.vehiculo.save(update_fields=['kilometraje'])
            actualizar_estado_vehiculo(reserva.vehiculo)
            _notificar_entrega(reserva)
            messages.success(request, f'Entrega de la reserva #{reserva.pk} registrada.')
            return redirect('reservas:lista')
    else:
        initial = {}
        if not reserva.km_entrega:
            initial['km_entrega'] = reserva.vehiculo.kilometraje
        form = EntregaForm(instance=reserva, initial=initial)

    return render(request, 'reservas/entrega.html', {
        'page_title': 'Registrar entrega',
        'page_subtitle': f'Reserva #{reserva.pk} · {reserva.vehiculo.placa}',
        'form': form,
        'reserva': reserva,
    })


def devolucion(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente', 'vehiculo'),
        pk=pk,
    )

    if not reserva.puede_registrar_devolucion:
        messages.warning(request, 'Esta reserva no está lista para registrar devolución.')
        return redirect('reservas:editar', pk=pk)

    if not reserva.entrega_registrada:
        messages.warning(request, 'Primero registra la entrega del vehículo.')
        return redirect('reservas:entrega', pk=pk)

    if request.method == 'POST':
        form = DevolucionForm(request.POST, request.FILES, instance=reserva)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.devolucion_registrada = True
            reserva.devolucion_registrada_en = timezone.now()
            reserva.estado = Reserva.Estado.COMPLETADA
            reserva.save()
            reserva.vehiculo.kilometraje = reserva.km_devolucion
            reserva.vehiculo.save(update_fields=['kilometraje'])
            actualizar_estado_vehiculo(reserva.vehiculo)
            _notificar_devolucion(reserva)
            messages.success(request, f'Devolución de la reserva #{reserva.pk} registrada.')
            return redirect('reservas:lista')
    else:
        initial = {}
        if not reserva.km_devolucion:
            initial['km_devolucion'] = reserva.km_entrega or reserva.vehiculo.kilometraje
        form = DevolucionForm(instance=reserva, initial=initial)

    return render(request, 'reservas/devolucion.html', {
        'page_title': 'Registrar devolución',
        'page_subtitle': f'Reserva #{reserva.pk} · {reserva.vehiculo.placa}',
        'form': form,
        'reserva': reserva,
    })
