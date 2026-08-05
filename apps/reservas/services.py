from django.utils import timezone

from apps.vehiculos.models import Vehiculo

from .models import Reserva


def actualizar_estados_reservas():
    """Pasa reservas a Activa o Completada según las fechas del calendario."""
    hoy = timezone.localdate()
    vehiculos_afectados = set()
    actualizadas = 0

    por_completar = Reserva.objects.filter(
        fecha_fin__lt=hoy,
    ).exclude(
        estado__in=[Reserva.Estado.CANCELADA, Reserva.Estado.COMPLETADA],
    )
    for reserva in por_completar:
        reserva.estado = Reserva.Estado.COMPLETADA
        reserva.save(update_fields=['estado'])
        vehiculos_afectados.add(reserva.vehiculo_id)
        actualizadas += 1

    por_activar = Reserva.objects.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy,
        estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA],
    )
    for reserva in por_activar:
        reserva.estado = Reserva.Estado.ACTIVA
        reserva.save(update_fields=['estado'])
        vehiculos_afectados.add(reserva.vehiculo_id)
        actualizadas += 1

    for vehiculo_id in vehiculos_afectados:
        try:
            vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
            actualizar_estado_vehiculo(vehiculo)
        except Vehiculo.DoesNotExist:
            pass

    return actualizadas


def actualizar_estado_vehiculo(vehiculo):
    """Sincroniza el estado del vehículo según reservas activas del día."""
    if vehiculo.estado == Vehiculo.Estado.MANTENIMIENTO:
        en_mantenimiento = vehiculo.mantenimientos.filter(
            estado__in=['programado', 'en_proceso'],
        ).exists()
        if en_mantenimiento:
            return

    hoy = timezone.localdate()
    rentado = Reserva.objects.filter(
        vehiculo=vehiculo,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy,
    ).exclude(
        estado__in=[Reserva.Estado.CANCELADA, Reserva.Estado.COMPLETADA],
    ).exists()

    nuevo_estado = Vehiculo.Estado.RENTADO if rentado else Vehiculo.Estado.DISPONIBLE
    if vehiculo.estado != nuevo_estado:
        vehiculo.estado = nuevo_estado
        vehiculo.save(update_fields=['estado'])
