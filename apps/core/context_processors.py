from django.conf import settings

from .permisos import MODULOS, modulos_usuario, rol_usuario


def panel_usuario(request):
    context = {
        'empresa_nombre': getattr(settings, 'EMPRESA_NOMBRE', 'Rent Car'),
        'panel_path': getattr(settings, 'PANEL_PATH', 'panel'),
        'alertas_reservas_web_count': 0,
        'alertas_reservas_web': [],
    }
    if request.user.is_authenticated:
        nombre = request.user.get_full_name() or request.user.username
        partes = nombre.split()
        if len(partes) >= 2:
            iniciales = f'{partes[0][0]}{partes[1][0]}'.upper()
        else:
            iniciales = nombre[:2].upper()
        context['usuario_nombre'] = nombre
        context['usuario_iniciales'] = iniciales
        context['usuario_rol'] = rol_usuario(request.user)
        modulos = modulos_usuario(request.user)
        context['menu_permisos'] = {clave: clave in modulos for clave in MODULOS}

        from apps.reservas.models import Reserva
        alertas_qs = Reserva.objects.filter(
            requiere_contacto_web=True,
            origen=Reserva.Origen.WEB,
        ).exclude(
            estado=Reserva.Estado.CANCELADA,
        ).select_related('cliente', 'vehiculo').order_by('-creado_en')
        context['alertas_reservas_web_count'] = alertas_qs.count()
        context['alertas_reservas_web'] = alertas_qs[:8]
    return context
