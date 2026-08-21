"""Traducciones del sitio público (ES/EN) sin depender de gettext.

Este servidor no tiene instaladas las herramientas de GNU gettext que
Django usa normalmente para traducciones (`{% trans %}` + archivos
.po/.mo), y muchos hostings compartidos tampoco las tienen. Por eso el
sitio público usa este diccionario propio en vez del sistema estándar
de Django: no depende de nada externo y funciona en cualquier servidor.

El idioma se guarda en una cookie (no en el prefijo de la URL) para no
romper las URLs ya indexadas por Google.
"""

IDIOMAS = [('es', 'Español'), ('en', 'English')]
IDIOMA_DEFECTO = 'es'
COOKIE_IDIOMA = 'idioma'

TEXTOS = {
    # Navegación / estructura
    'nav_inicio': {'es': 'Inicio', 'en': 'Home'},
    'nav_vehiculos': {'es': 'Vehículos', 'en': 'Vehicles'},
    'nav_ir_panel': {'es': 'Ir al panel', 'en': 'Go to panel'},
    'footer_ver_flota': {'es': 'Ver flota', 'en': 'View fleet'},
    'footer_siguenos': {'es': 'Síguenos', 'en': 'Follow us'},
    'footer_desarrollado_por': {'es': 'Desarrollado por', 'en': 'Powered by'},

    # Home
    'home_lead_defecto': {
        'es': 'Alquiler de vehículos con reserva online, tarifas claras y flota verificada.',
        'en': 'Vehicle rental with online booking, clear rates and a verified fleet.',
    },
    'home_ver_disponibles': {'es': 'Ver vehículos disponibles', 'en': 'See available vehicles'},
    'home_reservar_whatsapp': {'es': 'Reservar por WhatsApp', 'en': 'Book via WhatsApp'},
    'home_por_que_titulo': {'es': '¿Por qué reservar con nosotros?', 'en': 'Why book with us?'},
    'home_beneficio_1': {'es': 'Disponibilidad real por vehículo y fecha', 'en': 'Real-time availability by vehicle and date'},
    'home_beneficio_2': {'es': 'Reserva online en minutos', 'en': 'Book online in minutes'},
    'home_beneficio_3': {'es': 'SUV, sedán, pick-up, van y más', 'en': 'SUVs, sedans, pickups, vans and more'},
    'home_beneficio_4': {'es': 'Atención personalizada', 'en': 'Personalized service'},
    'home_por_whatsapp': {'es': ' por WhatsApp', 'en': ' via WhatsApp'},
    'home_explorar_flota': {'es': 'Explorar flota', 'en': 'Explore fleet'},
    'home_elige_categoria': {'es': 'Elige por categoría', 'en': 'Choose by category'},
    'home_elige_categoria_sub': {'es': 'Encuentra el vehículo ideal para tu viaje o negocio.', 'en': 'Find the ideal vehicle for your trip or business.'},
    'home_ver': {'es': 'Ver', 'en': 'View'},
    'home_destacados_titulo': {'es': 'Vehículos destacados', 'en': 'Featured vehicles'},
    'home_destacados_sub': {'es': 'Los más solicitados de nuestra flota.', 'en': 'The most requested in our fleet.'},
    'home_ver_toda_flota': {'es': 'Ver toda la flota', 'en': 'View entire fleet'},
    'home_cta_titulo': {'es': '¿Listo para tu próximo viaje?', 'en': 'Ready for your next trip?'},
    'home_cta_sub': {'es': 'Consulta disponibilidad, compara vehículos y reserva el que necesitas hoy.', 'en': 'Check availability, compare vehicles and book the one you need today.'},
    'home_ver_vehiculos': {'es': 'Ver vehículos', 'en': 'View vehicles'},
    'home_vehiculo_disponible': {'es': 'vehículo disponible para renta', 'en': 'vehicle available for rent'},
    'home_vehiculos_disponibles': {'es': 'vehículos disponibles para renta', 'en': 'vehicles available for rent'},
    'badge_24h': {'es': 'Atención 24 horas', 'en': '24-hour service'},
    'badge_aeropuertos': {'es': 'Entrega en todos los aeropuertos de RD', 'en': 'Delivery to all DR airports'},
    'badge_resenas': {'es': 'reseñas en Google', 'en': 'Google reviews'},

    # Flota (catálogo)
    'flota_titulo': {'es': 'Alquiler de vehículos — nuestra flota', 'en': 'Vehicle rental — our fleet'},
    'flota_lead': {'es': 'Filtra por categoría, transmisión o disponibilidad.', 'en': 'Filter by category, transmission or availability.'},
    'flota_todas_categorias': {'es': 'Todas las categorías', 'en': 'All categories'},
    'flota_transmision': {'es': 'Transmisión', 'en': 'Transmission'},
    'flota_filtrar': {'es': 'Filtrar', 'en': 'Filter'},
    'flota_limpiar': {'es': 'Limpiar', 'en': 'Clear'},
    'flota_sin_foto': {'es': 'Sin foto', 'en': 'No photo'},
    'flota_dia': {'es': '/ día', 'en': '/ day'},
    'flota_anterior': {'es': '← Anterior', 'en': '← Previous'},
    'flota_siguiente': {'es': 'Siguiente →', 'en': 'Next →'},
    'flota_pagina_de': {'es': 'Página {n} de {total}', 'en': 'Page {n} of {total}'},
    'flota_vacio': {'es': 'No hay vehículos con esos filtros. Prueba otras fechas o categorías.', 'en': 'No vehicles match those filters. Try different dates or categories.'},

    # Categorías / transmisión (por valor del modelo)
    'cat_sedan': {'es': 'Sedán', 'en': 'Sedan'},
    'cat_suv': {'es': 'SUV', 'en': 'SUV'},
    'cat_pickup': {'es': 'Pick-up', 'en': 'Pickup'},
    'cat_van': {'es': 'Van', 'en': 'Van'},
    'cat_lujo': {'es': 'Lujo', 'en': 'Luxury'},
    'trans_manual': {'es': 'Manual', 'en': 'Manual'},
    'trans_automatico': {'es': 'Automático', 'en': 'Automatic'},
    'trans_cvt': {'es': 'CVT', 'en': 'CVT'},

    # Ficha de vehículo
    'veh_volver_flota': {'es': '← Volver a la flota', 'en': '← Back to fleet'},
    'veh_descripcion': {'es': 'Descripción', 'en': 'Description'},
    'veh_ficha_tecnica': {'es': 'Ficha técnica', 'en': 'Specifications'},
    'veh_marca': {'es': 'Marca', 'en': 'Make'},
    'veh_modelo': {'es': 'Modelo', 'en': 'Model'},
    'veh_anio': {'es': 'Año', 'en': 'Year'},
    'veh_codigo': {'es': 'Código', 'en': 'Code'},
    'veh_categoria': {'es': 'Categoría', 'en': 'Category'},
    'veh_transmision': {'es': 'Transmisión', 'en': 'Transmission'},
    'veh_color': {'es': 'Color', 'en': 'Color'},
    'veh_kilometraje': {'es': 'Kilometraje', 'en': 'Mileage'},
    'veh_estado': {'es': 'Estado', 'en': 'Status'},
    'veh_disponible': {'es': 'Disponible', 'en': 'Available'},
    'veh_tarifa_diaria': {'es': 'Tarifa diaria', 'en': 'Daily rate'},
    'veh_estimado_7': {'es': 'Estimado 7 días', 'en': 'Estimated 7 days'},
    'veh_estimado_30': {'es': 'Estimado 30 días', 'en': 'Estimated 30 days'},
    'veh_condiciones_titulo': {'es': 'Condiciones de alquiler', 'en': 'Rental conditions'},
    'veh_condicion_anticipacion': {'es': 'Reserva con mínimo {h} horas de anticipación', 'en': 'Book at least {h} hours in advance'},
    'veh_condicion_confirmacion_auto': {'es': 'Confirmación automática al reservar', 'en': 'Automatic confirmation when booking'},
    'veh_condicion_confirmacion_manual': {'es': 'Confirmación por teléfono o WhatsApp tras la solicitud', 'en': 'Confirmation by phone or WhatsApp after your request'},
    'veh_condicion_horario': {'es': 'Horario', 'en': 'Hours'},
    'veh_condicion_documentos': {'es': 'Documento de identidad y licencia vigente requeridos', 'en': 'Valid ID and driver’s license required'},
    'veh_incluye_titulo': {'es': 'Incluye', 'en': 'Includes'},
    'veh_incluye_1': {'es': 'Vehículo en condiciones de circulación', 'en': 'Vehicle in roadworthy condition'},
    'veh_incluye_2': {'es': 'Documentación al día', 'en': 'Up-to-date documentation'},
    'veh_incluye_3': {'es': 'Asistencia de', 'en': 'Support from'},
    'veh_contacto_titulo': {'es': 'Contacto', 'en': 'Contact'},
    'veh_direccion': {'es': 'Dirección', 'en': 'Address'},
    'veh_telefono': {'es': 'Teléfono', 'en': 'Phone'},
    'veh_consultar_whatsapp': {'es': 'Consultar por WhatsApp', 'en': 'Ask on WhatsApp'},
    'veh_reservar': {'es': 'Reservar ahora', 'en': 'Book now'},
    'veh_no_disponible': {'es': 'No disponible en línea', 'en': 'Not available online'},
    'veh_relacionados_ver': {'es': 'Ver todos', 'en': 'View all'},
    'veh_dia': {'es': '/ día', 'en': '/ day'},

    # Reserva
    'res_titulo': {'es': 'Reservar', 'en': 'Book'},
    'res_volver': {'es': 'Volver', 'en': 'Back'},
    'res_enviar': {'es': 'Enviar reserva', 'en': 'Submit booking'},
    'res_campo_vehiculo': {'es': 'Vehículo', 'en': 'Vehicle'},
    'res_campo_fecha_inicio': {'es': 'Fecha de inicio', 'en': 'Start date'},
    'res_campo_fecha_fin': {'es': 'Fecha de fin', 'en': 'End date'},
    'res_campo_nombre': {'es': 'Nombre', 'en': 'First name'},
    'res_campo_apellido': {'es': 'Apellido', 'en': 'Last name'},
    'res_campo_documento': {'es': 'Cédula / Pasaporte', 'en': 'ID / Passport'},
    'res_campo_telefono': {'es': 'Teléfono', 'en': 'Phone'},
    'res_campo_email': {'es': 'Correo (opcional)', 'en': 'Email (optional)'},
    'res_campo_licencia_numero': {'es': 'Número de licencia', 'en': 'License number'},
    'res_campo_licencia_vence': {'es': 'Vencimiento de licencia', 'en': 'License expiration'},
    'res_campo_notas': {'es': 'Notas (opcional)', 'en': 'Notes (optional)'},
    'res_exito_listo': {'es': '¡Listo!', 'en': 'All set!'},
    'res_exito_registrada': {'es': 'Reserva #{n} registrada.', 'en': 'Booking #{n} received.'},
    'res_exito_volver_inicio': {'es': 'Volver al inicio', 'en': 'Back to home'},
    'res_exito_confirmar_whatsapp': {'es': 'Confirmar por WhatsApp', 'en': 'Confirm via WhatsApp'},
}


def idioma_actual(request):
    idioma = request.COOKIES.get(COOKIE_IDIOMA, IDIOMA_DEFECTO)
    return idioma if idioma in ('es', 'en') else IDIOMA_DEFECTO


def texto(clave, idioma, **kwargs):
    entrada = TEXTOS.get(clave)
    if not entrada:
        return clave
    valor = entrada.get(idioma) or entrada.get('es', clave)
    if kwargs:
        try:
            return valor.format(**kwargs)
        except (KeyError, IndexError):
            return valor
    return valor


def texto_categoria(valor_categoria, idioma):
    return texto(f'cat_{valor_categoria}', idioma) if valor_categoria else ''


def texto_transmision(valor_transmision, idioma):
    return texto(f'trans_{valor_transmision}', idioma) if valor_transmision else ''
