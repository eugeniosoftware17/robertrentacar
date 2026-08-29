from datetime import time, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.utils import timezone


def contexto_contrato_demo(empresa=None):
    """Datos ficticios para previsualizar el contrato con la config actual."""
    if empresa is None:
        from .models import ConfiguracionEmpresa

        empresa = ConfiguracionEmpresa.obtener()

    from apps.reservas.models import Reserva
    from apps.sitio.models import ConfiguracionSitio

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
        color='Gris plata',
    )
    cliente = SimpleNamespace(
        nombre_completo='Juan Pérez',
        documento='001-0000000-0',
        pasaporte='',
        telefono='809-555-0100',
        direccion='Calle Principal #10, Santo Domingo',
        nacionalidad='Dominicana',
        ocupacion='Ingeniero',
        lugar_expedicion='Santo Domingo',
        licencia_numero='L-123456',
        licencia_vence=hoy + timedelta(days=365),
    )
    conductor_adicional = SimpleNamespace(
        nombre_completo='John Smith',
        documento='',
        pasaporte='US123456789',
        telefono='+1 305-555-0100',
        direccion='Miami, FL, USA',
        nacionalidad='Estadounidense',
        ocupacion='Turista',
        lugar_expedicion='Florida, USA',
        licencia_numero='FL-998877',
        licencia_vence=hoy + timedelta(days=200),
    )
    checklist_marcados = [clave for clave, _ in Reserva.CHECKLIST_ITEMS[:16]]
    pago_deposito = SimpleNamespace(
        metodo='tarjeta',
        get_metodo_display=lambda: 'Tarjeta',
        tarjeta_tipo='Visa',
        tarjeta_ultimos4='4242',
        tarjeta_vencimiento='08/27',
        tarjeta_autorizacion='',
    )
    reserva = SimpleNamespace(
        pk=0,
        creado_en=timezone.now(),
        cliente=cliente,
        vehiculo=vehiculo,
        conductor_adicional=conductor_adicional,
        fecha_inicio=inicio,
        fecha_fin=fin,
        hora_entrega=time(9, 0),
        hora_devolucion=time(17, 0),
        lugar_entrega='Sucursal principal',
        lugar_devolucion='Sucursal principal',
        dias=dias,
        precio_total=precio,
        deposito=deposito,
        deducible=Decimal('8000.00'),
        posible_retorno=None,
        km_entrega=45230,
        combustible_entrega='lleno',
        get_combustible_entrega_display=lambda: 'Lleno',
        checklist_entrega=checklist_marcados,
        CHECKLIST_ITEMS=Reserva.CHECKLIST_ITEMS,
        pago_deposito=pago_deposito,
        total_pagado=deposito,
        saldo_pendiente=precio - deposito,
        notas='Reserva de ejemplo para vista previa del contrato.',
    )

    return {
        'empresa': empresa,
        'sitio': ConfiguracionSitio.obtener(),
        'reserva': reserva,
        'es_demo': True,
    }
