from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import paginar_queryset

from .forms import ClienteForm
from .models import Cliente


def lista(request):
    busqueda = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()

    if busqueda:
        clientes = clientes.filter(
            Q(nombre__icontains=busqueda)
            | Q(apellido__icontains=busqueda)
            | Q(documento__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
            | Q(email__icontains=busqueda)
        )

    page_obj = paginar_queryset(request, clientes)
    query_string = request.GET.copy()
    query_string.pop('page', None)
    query_string = query_string.urlencode()

    return render(request, 'clientes/lista.html', {
        'page_title': 'Clientes',
        'page_subtitle': 'Gestión de clientes registrados',
        'clientes': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'busqueda': busqueda,
        'total': clientes.count(),
    })


def crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre_completo} creado correctamente.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm()

    return render(request, 'clientes/formulario.html', {
        'page_title': 'Nuevo cliente',
        'page_subtitle': 'Registrar un cliente en el sistema',
        'form': form,
        'accion': 'crear',
    })


def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {cliente.nombre_completo} actualizado.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/formulario.html', {
        'page_title': 'Editar cliente',
        'page_subtitle': cliente.nombre_completo,
        'form': form,
        'accion': 'editar',
        'cliente': cliente,
    })


def eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        nombre = cliente.nombre_completo
        try:
            cliente.delete()
            messages.success(request, f'Cliente {nombre} eliminado.')
        except ProtectedError:
            messages.error(request, f'No se puede eliminar a {nombre}: tiene reservas asociadas.')
        return redirect('clientes:lista')

    return render(request, 'clientes/confirmar_eliminar.html', {
        'page_title': 'Eliminar cliente',
        'page_subtitle': cliente.nombre_completo,
        'cliente': cliente,
    })
