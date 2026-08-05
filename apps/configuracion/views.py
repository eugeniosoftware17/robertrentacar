from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.permisos import es_admin

from .forms import ConfiguracionForm, PermisosEmpleadoForm
from .models import ConfiguracionEmpresa


def index(request):
    config = ConfiguracionEmpresa.obtener()
    permisos_form = PermisosEmpleadoForm.desde_bd()

    if request.method == 'POST':
        if 'guardar_empresa' in request.POST:
            form = ConfiguracionForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, 'Configuración guardada.')
                return redirect('configuracion:index')
        elif 'guardar_permisos' in request.POST and es_admin(request.user):
            permisos_form = PermisosEmpleadoForm(request.POST)
            if permisos_form.is_valid():
                permisos_form.guardar()
                messages.success(request, 'Permisos de empleados actualizados.')
                return redirect('configuracion:index')
        else:
            form = ConfiguracionForm(instance=config)
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, 'configuracion/index.html', {
        'page_title': 'Configuración',
        'page_subtitle': 'Datos de la empresa y permisos',
        'form': form,
        'permisos_form': permisos_form,
        'puede_editar_permisos': es_admin(request.user),
        'empresa_env': getattr(settings, 'EMPRESA_NOMBRE', ''),
    })
