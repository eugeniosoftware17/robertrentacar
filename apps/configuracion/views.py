from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import requiere_modulo
from apps.core.permisos import es_admin_sistema, rol_usuario

from .contrato_demo import contexto_contrato_demo
from .forms import (
    ConfiguracionForm,
    CrearUsuarioPanelForm,
    EditarUsuarioPanelForm,
    PermisosEmpleadoForm,
)
from .models import ConfiguracionEmpresa

User = get_user_model()


def _usuarios_panel():
    return User.objects.filter(is_superuser=False).order_by('username')


@requiere_modulo('configuracion')
def index(request):
    if not es_admin_sistema(request.user):
        return render(request, '403.html', {
            'page_title': 'Acceso denegado',
            'modulo': 'configuracion',
        }, status=403)

    config = ConfiguracionEmpresa.obtener()
    permisos_form = PermisosEmpleadoForm.desde_bd()
    puede_gestionar_sistema = request.user.is_superuser
    crear_usuario_form = CrearUsuarioPanelForm(puede_crear_sistema=puede_gestionar_sistema)
    editar_usuario = None
    editar_usuario_form = None

    editar_id = request.GET.get('usuario')
    if editar_id:
        editar_usuario = get_object_or_404(User, pk=editar_id, is_superuser=False)
        editar_usuario_form = EditarUsuarioPanelForm(
            usuario=editar_usuario,
            puede_asignar_sistema=puede_gestionar_sistema,
        )

    if request.method == 'POST':
        if 'guardar_empresa' in request.POST:
            form = ConfiguracionForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, 'Configuración guardada.')
                return redirect('configuracion:index')
        elif 'guardar_permisos' in request.POST:
            permisos_form = PermisosEmpleadoForm(request.POST)
            if permisos_form.is_valid():
                permisos_form.guardar()
                messages.success(request, 'Permisos de empleados actualizados.')
                return redirect('configuracion:index')
        elif 'crear_usuario' in request.POST:
            crear_usuario_form = CrearUsuarioPanelForm(
                request.POST,
                puede_crear_sistema=puede_gestionar_sistema,
            )
            if crear_usuario_form.is_valid():
                user = crear_usuario_form.guardar()
                messages.success(request, f'Usuario «{user.username}» creado.')
                return redirect('configuracion:index')
        elif 'editar_usuario' in request.POST:
            editar_usuario = get_object_or_404(
                User,
                pk=request.POST.get('usuario_id'),
                is_superuser=False,
            )
            editar_usuario_form = EditarUsuarioPanelForm(
                request.POST,
                usuario=editar_usuario,
                puede_asignar_sistema=puede_gestionar_sistema,
            )
            if editar_usuario_form.is_valid():
                editar_usuario_form.guardar()
                messages.success(request, f'Usuario «{editar_usuario.username}» actualizado.')
                return redirect('configuracion:index')
        else:
            form = ConfiguracionForm(instance=config)
    else:
        form = ConfiguracionForm(instance=config)

    usuarios_panel = [
        {'usuario': usuario, 'rol': rol_usuario(usuario)}
        for usuario in _usuarios_panel()
    ]

    return render(request, 'configuracion/index.html', {
        'page_title': 'Configuración',
        'page_subtitle': 'Datos de la empresa, usuarios y permisos',
        'form': form,
        'permisos_form': permisos_form,
        'crear_usuario_form': crear_usuario_form,
        'editar_usuario': editar_usuario,
        'editar_usuario_form': editar_usuario_form,
        'usuarios_panel': usuarios_panel,
        'empresa_env': getattr(settings, 'EMPRESA_NOMBRE', ''),
    })


@requiere_modulo('configuracion')
def contrato_demo(request):
    if not es_admin_sistema(request.user):
        return render(request, '403.html', {
            'page_title': 'Acceso denegado',
            'modulo': 'configuracion',
        }, status=403)

    return render(request, 'reservas/contrato.html', contexto_contrato_demo())
