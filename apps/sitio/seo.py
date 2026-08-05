from django.urls import reverse


def meta_descripcion_home(empresa, sitio):
    if sitio.meta_descripcion:
        return sitio.meta_descripcion
    partes = [
        f'Alquiler de vehículos en {empresa.nombre}.',
        sitio.home_subtitulo or 'SUV, sedán, pick-up y más.',
        'Reserva online con disponibilidad real.',
    ]
    texto = ' '.join(p for p in partes if p)
    return texto[:160]


def meta_descripcion_vehiculo(vehiculo, empresa):
    base = (
        f'Alquila {vehiculo.nombre_corto} desde RD$ {vehiculo.tarifa_diaria:,.0f}/día '
        f'en {empresa.nombre}. {vehiculo.get_categoria_display()}, '
        f'{vehiculo.get_transmision_display()}. Reserva en línea.'
    )
    if vehiculo.descripcion_web:
        extra = vehiculo.descripcion_web.strip()
        if extra:
            base = f'{base} {extra}'
    return base[:160]


def meta_descripcion_flota(empresa):
    return (
        f'Flota completa de {empresa.nombre}: alquiler de carros por día. '
        f'Filtra por categoría, transmisión y fechas. Reserva online.'
    )[:160]
