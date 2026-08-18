from decimal import Decimal

from django.contrib import messages
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.utils import paginar_queryset

from .forms import EmpleadoForm, GastoForm, PagoNominaForm
from .models import Empleado, Gasto, PagoNomina
from .utils import normalizar_rango, rango_mes_actual


def _aplicar_filtro_fecha(qs, campo_desde, campo_hasta, desde, hasta):
    if desde:
        qs = qs.filter(**{f'{campo_desde}__gte': desde})
    if hasta:
        qs = qs.filter(**{f'{campo_hasta}__lte': hasta})
    return qs


def _mensaje_rango_invertido(request, invertido):
    if invertido:
        messages.info(request, 'Las fechas estaban al revés; se corrigió el rango automáticamente.')


def index(request):
    inicio_mes, hoy = rango_mes_actual()
    rango = normalizar_rango(
        request.GET.get('desde'),
        request.GET.get('hasta'),
        desde_def=inicio_mes,
        hasta_def=hoy,
    )
    _mensaje_rango_invertido(request, rango['invertido'])

    nomina_periodo = _aplicar_filtro_fecha(
        PagoNomina.objects.all(), 'fecha_pago', 'fecha_pago', rango['desde'], rango['hasta'],
    )
    gastos_periodo = _aplicar_filtro_fecha(
        Gasto.objects.all(), 'fecha', 'fecha', rango['desde'], rango['hasta'],
    )

    total_nomina = nomina_periodo.aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    total_gastos = gastos_periodo.aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    gastos_vehiculo = gastos_periodo.filter(vehiculo__isnull=False).aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    gastos_generales = total_gastos - gastos_vehiculo

    return render(request, 'finanzas/index.html', {
        'page_title': 'Nómina y gastos',
        'page_subtitle': 'Pagos al personal y otros gastos del negocio',
        'desde': rango['desde_iso'],
        'hasta': rango['hasta_iso'],
        'total_nomina': total_nomina,
        'total_gastos': total_gastos,
        'gastos_vehiculo': gastos_vehiculo,
        'gastos_generales': gastos_generales,
        'total_general': total_nomina + total_gastos,
        'empleados_activos': Empleado.objects.filter(activo=True).count(),
        'pagos_periodo': nomina_periodo.count(),
        'gastos_cantidad': gastos_periodo.count(),
    })


# ——— Empleados ———

def empleados_lista(request):
    busqueda = request.GET.get('q', '').strip()
    empleados = Empleado.objects.all()
    if busqueda:
        empleados = empleados.filter(
            Q(nombre__icontains=busqueda) | Q(apellido__icontains=busqueda) | Q(puesto__icontains=busqueda)
        )

    page_obj = paginar_queryset(request, empleados)
    return render(request, 'finanzas/empleados_lista.html', {
        'page_title': 'Empleados',
        'page_subtitle': 'Personal del negocio',
        'empleados': page_obj,
        'page_obj': page_obj,
        'busqueda': busqueda,
        'total': empleados.count(),
    })


def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            empleado = form.save()
            messages.success(request, f'Empleado {empleado.nombre_completo} registrado.')
            return redirect('finanzas:empleados_lista')
    else:
        form = EmpleadoForm()

    return render(request, 'finanzas/empleado_formulario.html', {
        'page_title': 'Nuevo empleado',
        'form': form,
        'accion': 'crear',
    })


def empleado_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado.')
            return redirect('finanzas:empleados_lista')
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, 'finanzas/empleado_formulario.html', {
        'page_title': 'Editar empleado',
        'page_subtitle': empleado.nombre_completo,
        'form': form,
        'accion': 'editar',
        'empleado': empleado,
    })


def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        nombre = empleado.nombre_completo
        try:
            empleado.delete()
            messages.success(request, f'Empleado {nombre} eliminado.')
        except ProtectedError:
            messages.error(request, f'No se puede eliminar a {nombre}: tiene pagos de nómina registrados.')
        return redirect('finanzas:empleados_lista')

    return render(request, 'finanzas/empleado_confirmar_eliminar.html', {
        'page_title': 'Eliminar empleado',
        'page_subtitle': empleado.nombre_completo,
        'empleado': empleado,
    })


# ——— Nómina ———

def nomina_lista(request):
    empleado_id = request.GET.get('empleado', '')
    inicio_mes, hoy = rango_mes_actual()

    if empleado_id and 'desde' not in request.GET:
        # Historial completo de un empleado concreto.
        rango = normalizar_rango('', request.GET.get('hasta'), hasta_def=hoy)
    else:
        rango = normalizar_rango(
            request.GET.get('desde'),
            request.GET.get('hasta'),
            desde_def=inicio_mes,
            hasta_def=hoy,
        )
    _mensaje_rango_invertido(request, rango['invertido'])

    pagos = PagoNomina.objects.select_related('empleado').all()
    pagos = _aplicar_filtro_fecha(pagos, 'fecha_pago', 'fecha_pago', rango['desde'], rango['hasta'])
    if empleado_id:
        pagos = pagos.filter(empleado_id=empleado_id)

    total = pagos.aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    page_obj = paginar_queryset(request, pagos)

    return render(request, 'finanzas/nomina_lista.html', {
        'page_title': 'Nómina',
        'page_subtitle': 'Pagos registrados al personal',
        'pagos': page_obj,
        'page_obj': page_obj,
        'desde': rango['desde_iso'],
        'hasta': rango['hasta_iso'],
        'historial_completo': bool(empleado_id and not rango['desde']),
        'empleado_filtro': empleado_id,
        'empleados': Empleado.objects.order_by('-activo', 'apellido', 'nombre'),
        'total': total,
        'cantidad': pagos.count(),
    })


def nomina_crear(request):
    if request.method == 'POST':
        form = PagoNominaForm(request.POST)
        if form.is_valid():
            pago = form.save()
            messages.success(request, f'Pago registrado para {pago.empleado.nombre_completo}.')
            return redirect('finanzas:nomina_lista')
    else:
        initial = {'fecha_pago': timezone.localdate()}
        empleado_id = request.GET.get('empleado')
        if empleado_id:
            initial['empleado'] = empleado_id
        form = PagoNominaForm(initial=initial)

    return render(request, 'finanzas/nomina_formulario.html', {
        'page_title': 'Nuevo pago de nómina',
        'form': form,
        'accion': 'crear',
    })


def nomina_editar(request, pk):
    pago = get_object_or_404(PagoNomina, pk=pk)
    if request.method == 'POST':
        form = PagoNominaForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago actualizado.')
            return redirect('finanzas:nomina_lista')
    else:
        form = PagoNominaForm(instance=pago)

    return render(request, 'finanzas/nomina_formulario.html', {
        'page_title': 'Editar pago de nómina',
        'page_subtitle': str(pago),
        'form': form,
        'accion': 'editar',
        'pago': pago,
    })


def nomina_eliminar(request, pk):
    pago = get_object_or_404(PagoNomina, pk=pk)
    if request.method == 'POST':
        pago.delete()
        messages.success(request, 'Pago de nómina eliminado.')
        return redirect('finanzas:nomina_lista')

    return render(request, 'finanzas/nomina_confirmar_eliminar.html', {
        'page_title': 'Eliminar pago de nómina',
        'page_subtitle': str(pago),
        'pago': pago,
    })


# ——— Gastos ———

def gastos_lista(request):
    inicio_mes, hoy = rango_mes_actual()
    rango = normalizar_rango(
        request.GET.get('desde'),
        request.GET.get('hasta'),
        desde_def=inicio_mes,
        hasta_def=hoy,
    )
    _mensaje_rango_invertido(request, rango['invertido'])
    categoria = request.GET.get('categoria', '')

    gastos = Gasto.objects.select_related('vehiculo').all()
    gastos = _aplicar_filtro_fecha(gastos, 'fecha', 'fecha', rango['desde'], rango['hasta'])
    if categoria:
        gastos = gastos.filter(categoria=categoria)

    total = gastos.aggregate(t=Sum('monto'))['t'] or Decimal('0.00')
    page_obj = paginar_queryset(request, gastos)

    return render(request, 'finanzas/gastos_lista.html', {
        'page_title': 'Gastos',
        'page_subtitle': 'Gastos adicionales del negocio',
        'gastos': page_obj,
        'page_obj': page_obj,
        'desde': rango['desde_iso'],
        'hasta': rango['hasta_iso'],
        'categoria_filtro': categoria,
        'categorias': Gasto.Categoria.choices,
        'total': total,
        'cantidad': gastos.count(),
    })


def gasto_crear(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto registrado.')
            return redirect('finanzas:gastos_lista')
    else:
        initial = {'fecha': timezone.localdate()}
        vehiculo_id = request.GET.get('vehiculo')
        if vehiculo_id:
            initial['vehiculo'] = vehiculo_id
        form = GastoForm(initial=initial)

    return render(request, 'finanzas/gasto_formulario.html', {
        'page_title': 'Nuevo gasto',
        'form': form,
        'accion': 'crear',
    })


def gasto_editar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto actualizado.')
            return redirect('finanzas:gastos_lista')
    else:
        form = GastoForm(instance=gasto)

    return render(request, 'finanzas/gasto_formulario.html', {
        'page_title': 'Editar gasto',
        'page_subtitle': gasto.concepto,
        'form': form,
        'accion': 'editar',
        'gasto': gasto,
    })


def gasto_eliminar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto eliminado.')
        return redirect('finanzas:gastos_lista')

    return render(request, 'finanzas/gasto_confirmar_eliminar.html', {
        'page_title': 'Eliminar gasto',
        'page_subtitle': gasto.concepto,
        'gasto': gasto,
    })
