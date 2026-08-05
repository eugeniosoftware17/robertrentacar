from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import paginar_queryset

from .forms import MantenimientoForm
from .models import Mantenimiento


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    registros = Mantenimiento.objects.select_related('vehiculo')

    if busqueda:
        registros = registros.filter(
            Q(vehiculo__marca__icontains=busqueda)
            | Q(vehiculo__modelo__icontains=busqueda)
            | Q(vehiculo__placa__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
        )

    if estado:
        registros = registros.filter(estado=estado)

    page_obj = paginar_queryset(request, registros)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    return render(request, 'mantenimiento/lista.html', {
        'page_title': 'Mantenimiento',
        'page_subtitle': 'Servicios y revisiones de la flota',
        'registros': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'estado_filtro': estado,
        'estados': Mantenimiento.Estado.choices,
        'total': registros.count(),
    })


def crear(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            registro = form.save()
            messages.success(request, f'Mantenimiento registrado para {registro.vehiculo.placa}.')
            return redirect('mantenimiento:lista')
    else:
        initial = {}
        vehiculo_id = request.GET.get('vehiculo')
        if vehiculo_id:
            initial['vehiculo'] = vehiculo_id
        form = MantenimientoForm(initial=initial)

    return render(request, 'mantenimiento/formulario.html', {
        'page_title': 'Nuevo mantenimiento',
        'page_subtitle': 'Registrar servicio o revisión',
        'form': form,
        'accion': 'crear',
    })


def editar(request, pk):
    registro = get_object_or_404(Mantenimiento, pk=pk)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mantenimiento actualizado.')
            return redirect('mantenimiento:lista')
    else:
        form = MantenimientoForm(instance=registro)

    return render(request, 'mantenimiento/formulario.html', {
        'page_title': 'Editar mantenimiento',
        'page_subtitle': str(registro),
        'form': form,
        'accion': 'editar',
        'registro': registro,
    })


def eliminar(request, pk):
    registro = get_object_or_404(Mantenimiento, pk=pk)

    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(request, 'Registro de mantenimiento eliminado.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar este registro.')
        return redirect('mantenimiento:lista')

    return render(request, 'mantenimiento/confirmar_eliminar.html', {
        'page_title': 'Eliminar mantenimiento',
        'page_subtitle': str(registro),
        'registro': registro,
    })
