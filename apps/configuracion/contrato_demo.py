from datetime import time, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.utils import timezone


def contexto_contrato_demo(empresa=None):
    """Datos ficticios para previsualizar el contrato con la config actual."""
    if empresa is None:
        from .models import ConfiguracionEmpresa

        empresa = ConfiguracionEmpresa.obtener()

    hoy = timezone.localdate()
    inicio = hoy + timedelta(days=3)
    fin = hoy + timedelta(days=6)
    tarifa = Decimal('3500.00')
    dias = (fin - inicio).days + 1
    precio = tarifa * dias
    deposito = Decimal('5000.00')

    categoria = SimpleNamespace(nombre='SUV')
    vehiculo = SimpleNamespace(
        nombre_corto='Toyota RAV4 2023',
        placa='A123456',
        categoria=categoria,
        tarifa_diaria=tarifa,
    )
    cliente = SimpleNamespace(
        nombre_completo='Juan Pérez',
        documento='001-0000000-0',
        telefono='809-555-0100',
        licencia_numero='L-123456',
        licencia_vence=hoy + timedelta(days=365),
    )
    reserva = SimpleNamespace(
        pk=0,
        creado_en=timezone.now(),
        cliente=cliente,
        vehiculo=vehiculo,
        fecha_inicio=inicio,
        fecha_fin=fin,
        hora_entrega=time(9, 0),
        hora_devolucion=time(17, 0),
        lugar_entrega='Sucursal principal',
        lugar_devolucion='Sucursal principal',
        dias=dias,
        precio_total=precio,
        deposito=deposito,
        total_pagado=deposito,
        saldo_pendiente=precio - deposito,
        notas='Reserva de ejemplo para vista previa del contrato.',
    )

    return {
        'empresa': empresa,
        'reserva': reserva,
        'es_demo': True,
    }
