from decimal import Decimal


def resumen_financiero(vehiculo, desde=None, hasta=None):
    """Ingresos, gastos y ganancia neta de un vehículo, opcionalmente por rango de fechas."""
    from apps.finanzas.models import Gasto
    from apps.mantenimiento.models import Mantenimiento
    from apps.reservas.models import Reserva

    reservas = Reserva.objects.filter(vehiculo=vehiculo).exclude(estado=Reserva.Estado.CANCELADA)
    mantenimientos = Mantenimiento.objects.filter(vehiculo=vehiculo)
    gastos = Gasto.objects.filter(vehiculo=vehiculo)

    if desde:
        reservas = reservas.filter(fecha_inicio__gte=desde)
        mantenimientos = mantenimientos.filter(fecha__gte=desde)
        gastos = gastos.filter(fecha__gte=desde)
    if hasta:
        reservas = reservas.filter(fecha_inicio__lte=hasta)
        mantenimientos = mantenimientos.filter(fecha__lte=hasta)
        gastos = gastos.filter(fecha__lte=hasta)

    ingresos = sum((r.precio_total for r in reservas), Decimal('0.00'))
    gasto_mantenimiento = sum((m.costo for m in mantenimientos), Decimal('0.00'))
    gasto_adicional = sum((g.monto for g in gastos), Decimal('0.00'))
    gastos_totales = gasto_mantenimiento + gasto_adicional
    ganancia_operativa = ingresos - gastos_totales

    precio_compra = vehiculo.precio_compra or Decimal('0.00')
    ganancia_neta = ganancia_operativa - precio_compra
    porcentaje_recuperado = (
        min((ingresos / precio_compra) * 100, Decimal('999.9'))
        if precio_compra
        else None
    )

    return {
        'ingresos': ingresos,
        'gasto_mantenimiento': gasto_mantenimiento,
        'gasto_adicional': gasto_adicional,
        'gastos_totales': gastos_totales,
        'ganancia_operativa': ganancia_operativa,
        'precio_compra': precio_compra,
        'ganancia_neta': ganancia_neta,
        'porcentaje_recuperado': porcentaje_recuperado,
        'reservas_cantidad': reservas.count(),
        'mantenimientos_cantidad': mantenimientos.count(),
    }
