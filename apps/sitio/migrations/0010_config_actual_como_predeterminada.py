from decimal import Decimal

from django.db import migrations


def cargar_configuracion_actual(apps, schema_editor):
    ConfiguracionSitio = apps.get_model('sitio', 'ConfiguracionSitio')
    ConfiguracionSitio.objects.update_or_create(
        pk=1,
        defaults={
            'home_titulo': 'Robert Rent A Car',
            'home_titulo_en': 'Robert Rent A Car',
            'home_subtitulo': 'SUVs y carros nuevos, entrega en todos los aeropuertos de RD',
            'home_subtitulo_en': 'SUVs and new cars, delivery to all DR airports',
            'home_diseno': 'foto',
            'home_fondo_opacidad': 60,
            'home_fondo_posicion': 'center',
            'home_fondo_tamano': 'cover',
            'home_mostrar_panel': True,
            'home_mostrar_categorias': True,
            'home_mostrar_destacados': True,
            'home_mostrar_cta': True,
            'home_mostrar_contador': True,
            'home_mostrar_redes_hero': True,
            'mostrar_nombre_junto_logo': True,
            'servicio_24h': True,
            'entrega_aeropuertos': True,
            'mostrar_resenas': True,
            'resena_calificacion': Decimal('5.0'),
            'resena_cantidad': 14,
            'whatsapp': '+1 809-399-9540',
            'whatsapp_mensaje': 'Hola, me interesa alquilar un vehiculo. ¿Tienen disponibilidad?',
            'whatsapp_flotante': True,
            'mostrar_whatsapp': True,
            'horario': 'Atencion 24 horas',
            'instagram': 'https://www.instagram.com/robertrentacar',
            'mostrar_instagram': True,
            'facebook': 'https://www.facebook.com/share/17XmHCV6dJ/',
            'mostrar_facebook': True,
            'tiktok': 'https://www.tiktok.com/@robrt_04',
            'mostrar_tiktok': True,
            'reserva_auto_confirmar': False,
            'anticipacion_horas': 24,
            'bloquear_mantenimiento': True,
            'mensaje_reserva_exito': 'Gracias. Hemos recibido tu solicitud. Te contactaremos pronto para confirmar.',
        },
    )
    # La imagen de fondo del inicio (home_fondo_imagen) no se puede copiar
    # por migracion porque el archivo vive en media/, que no se sube al
    # repositorio. Hay que volver a subirla una vez desde el panel
    # (Sitio web > Inicio); el diseno, posicion y tamano ya quedan
    # configurados igual que en local.


def revertir(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0009_configuracionsitio_entrega_aeropuertos_and_more'),
    ]

    operations = [
        migrations.RunPython(cargar_configuracion_actual, revertir),
    ]
