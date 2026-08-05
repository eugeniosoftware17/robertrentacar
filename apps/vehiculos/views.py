from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import paginar_queryset

from .forms import VehiculoForm
from .models import Vehiculo, VehiculoFoto


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    vehiculos = Vehiculo.objects.all()

    if busqueda:
        vehiculos = vehiculos.filter(
            Q(marca__icontains=busqueda)
            | Q(modelo__icontains=busqueda)
            | Q(placa__icontains=busqueda)
            | Q(color__icontains=busqueda)
        )

    if estado:
        vehiculos = vehiculos.filter(estado=estado)

    page_obj = paginar_queryset(request, vehiculos)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    return render(request, 'vehiculos/lista.html', {
        'page_title': 'Vehículos',
        'page_subtitle': 'Flota de vehículos disponibles',
        'vehiculos': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'estado_filtro': estado,
        'estados': Vehiculo.Estado.choices,
        'total': vehiculos.count(),
    })


def crear(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f'Vehículo {vehiculo.nombre_corto} registrado.')
            return redirect('vehiculos:lista')
    else:
        form = VehiculoForm()

    return render(request, 'vehiculos/formulario.html', {
        'page_title': 'Nuevo vehículo',
        'page_subtitle': 'Agregar un vehículo a la flota',
        'form': form,
        'accion': 'crear',
    })


def _guardar_fotos_galeria(vehiculo, request):
    for orden in (1, 2, 3):
        key = f'foto_galeria_{orden}'
        eliminar = request.POST.get(f'eliminar_foto_galeria_{orden}')
        if eliminar:
            VehiculoFoto.objects.filter(vehiculo=vehiculo, orden=orden).delete()
            continue
        if key in request.FILES:
            VehiculoFoto.objects.update_or_create(
                vehiculo=vehiculo,
                orden=orden,
                defaults={'imagen': request.FILES[key]},
            )


def editar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            form.save()
            _guardar_fotos_galeria(vehiculo, request)
            messages.success(request, f'Vehículo {vehiculo.nombre_corto} actualizado.')
            return redirect('vehiculos:lista')
    else:
        form = VehiculoForm(instance=vehiculo)

    fotos = {f.orden: f for f in vehiculo.fotos_galeria.all()}
    galeria_slots = [{'orden': n, 'foto': fotos.get(n)} for n in (1, 2, 3)]

    return render(request, 'vehiculos/formulario.html', {
        'page_title': 'Editar vehículo',
        'page_subtitle': vehiculo.nombre_corto,
        'form': form,
        'accion': 'editar',
        'vehiculo': vehiculo,
        'galeria_slots': galeria_slots,
    })


def eliminar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)

    if request.method == 'POST':
        nombre = vehiculo.nombre_corto
        try:
            vehiculo.delete()
            messages.success(request, f'Vehículo {nombre} eliminado.')
        except ProtectedError:
            messages.error(request, f'No se puede eliminar {nombre}: tiene reservas o mantenimientos asociados.')
        return redirect('vehiculos:lista')

    return render(request, 'vehiculos/confirmar_eliminar.html', {
        'page_title': 'Eliminar vehículo',
        'page_subtitle': vehiculo.nombre_corto,
        'vehiculo': vehiculo,
    })
