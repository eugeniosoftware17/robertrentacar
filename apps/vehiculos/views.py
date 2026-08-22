from django.contrib import messages
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import paginar_queryset

from .forms import CategoriaVehiculoForm, VehiculoForm
from .models import CategoriaVehiculo, Vehiculo, VehiculoFoto
from .queries import filtrar_vehiculos
from .services import resumen_financiero


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    letra = request.GET.get('letra', '').strip().upper()[:1]
    estado = request.GET.get('estado', '')
    categoria_id = request.GET.get('categoria', '')

    vehiculos = Vehiculo.objects.select_related('categoria').all()
    vehiculos = filtrar_vehiculos(vehiculos, termino=busqueda, letra=letra)

    if estado:
        vehiculos = vehiculos.filter(estado=estado)
    if categoria_id:
        vehiculos = vehiculos.filter(categoria_id=categoria_id)

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
        'letra_filtro': letra,
        'estado_filtro': estado,
        'categoria_filtro': categoria_id,
        'estados': Vehiculo.Estado.choices,
        'categorias': CategoriaVehiculo.objects.order_by('orden', 'nombre'),
        'alfabeto': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'total': vehiculos.count(),
    })


def categorias_lista(request):
    categorias = CategoriaVehiculo.objects.annotate(
        total_vehiculos=Count('vehiculos'),
    ).order_by('orden', 'nombre')

    return render(request, 'vehiculos/categorias_lista.html', {
        'page_title': 'Categorías de vehículos',
        'page_subtitle': 'Tipos de vehículo para la flota y el sitio web',
        'categorias': categorias,
    })


def categoria_crear(request):
    if request.method == 'POST':
        form = CategoriaVehiculoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría «{categoria.nombre}» creada.')
            return redirect('vehiculos:categorias_lista')
    else:
        form = CategoriaVehiculoForm()

    return render(request, 'vehiculos/categoria_form.html', {
        'page_title': 'Nueva categoría',
        'page_subtitle': 'Agregar tipo de vehículo',
        'form': form,
        'accion': 'crear',
    })


def categoria_editar(request, pk):
    categoria = get_object_or_404(CategoriaVehiculo, pk=pk)

    if request.method == 'POST':
        form = CategoriaVehiculoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría «{categoria.nombre}» actualizada.')
            return redirect('vehiculos:categorias_lista')
    else:
        form = CategoriaVehiculoForm(instance=categoria)

    return render(request, 'vehiculos/categoria_form.html', {
        'page_title': 'Editar categoría',
        'page_subtitle': categoria.nombre,
        'form': form,
        'accion': 'editar',
        'categoria': categoria,
    })


def categoria_eliminar(request, pk):
    categoria = get_object_or_404(CategoriaVehiculo, pk=pk)

    if request.method == 'POST':
        nombre = categoria.nombre
        try:
            categoria.delete()
            messages.success(request, f'Categoría «{nombre}» eliminada.')
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar «{nombre}»: tiene vehículos asignados.',
            )
        return redirect('vehiculos:categorias_lista')

    return render(request, 'vehiculos/categoria_confirmar_eliminar.html', {
        'page_title': 'Eliminar categoría',
        'page_subtitle': categoria.nombre,
        'categoria': categoria,
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


def rentabilidad(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    desde = request.GET.get('desde') or ''
    hasta = request.GET.get('hasta') or ''
    resumen = resumen_financiero(vehiculo, desde=desde or None, hasta=hasta or None)

    return render(request, 'vehiculos/rentabilidad.html', {
        'page_title': 'Rentabilidad',
        'page_subtitle': vehiculo.nombre_corto,
        'vehiculo': vehiculo,
        'resumen': resumen,
        'desde': desde,
        'hasta': hasta,
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
