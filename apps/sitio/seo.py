from django.urls import reverse

from .i18n import IDIOMA_DEFECTO, texto, texto_categoria, texto_transmision


def meta_descripcion_home(empresa, sitio, idioma=IDIOMA_DEFECTO):
    if idioma == 'en' and sitio.meta_descripcion_en:
        return sitio.meta_descripcion_en
    if sitio.meta_descripcion:
        return sitio.meta_descripcion
    ciudad = empresa.ciudad or ''
    if idioma == 'en':
        partes = [
            f'Car rental in {ciudad}.' if ciudad else f'Car rental at {empresa.nombre}.',
            sitio.home_subtitulo_en or sitio.home_subtitulo or 'SUVs, sedans, pickups and more.',
            'Book online with real availability.',
        ]
    else:
        partes = [
            f'Alquiler de vehículos en {ciudad}.' if ciudad else f'Alquiler de vehículos en {empresa.nombre}.',
            sitio.home_subtitulo or 'SUV, sedán, pick-up y más.',
            'Reserva online con disponibilidad real.',
        ]
    texto_final = ' '.join(p for p in partes if p)
    return texto_final[:160]


def meta_descripcion_vehiculo(vehiculo, empresa, idioma=IDIOMA_DEFECTO):
    categoria = texto_categoria(vehiculo.categoria, idioma)
    transmision = texto_transmision(vehiculo.transmision, idioma)
    if idioma == 'en':
        lugar = f'in {empresa.ciudad}' if empresa.ciudad else f'at {empresa.nombre}'
        base = (
            f'Rent {vehiculo.nombre_corto} from USD$ {vehiculo.tarifa_diaria:,.0f}/day '
            f'{lugar}. {categoria}, {transmision}. Book online.'
        )
        extra = (vehiculo.descripcion_web_en or vehiculo.descripcion_web or '').strip()
    else:
        lugar = f'en {empresa.ciudad}' if empresa.ciudad else f'en {empresa.nombre}'
        base = (
            f'Alquila {vehiculo.nombre_corto} desde USD$ {vehiculo.tarifa_diaria:,.0f}/día '
            f'{lugar}. {categoria}, {transmision}. Reserva en línea.'
        )
        extra = (vehiculo.descripcion_web or '').strip()
    if extra:
        base = f'{base} {extra}'
    return base[:160]


def meta_descripcion_flota(empresa, idioma=IDIOMA_DEFECTO):
    if idioma == 'en':
        ciudad = f' in {empresa.ciudad}' if empresa.ciudad else ''
        return (
            f'Full fleet at {empresa.nombre}: daily car rental{ciudad}. '
            f'Filter by category, transmission and dates. Book online.'
        )[:160]
    ciudad = f' en {empresa.ciudad}' if empresa.ciudad else ''
    return (
        f'Flota completa de {empresa.nombre}: alquiler de carros por día{ciudad}. '
        f'Filtra por categoría, transmisión y fechas. Reserva online.'
    )[:160]
