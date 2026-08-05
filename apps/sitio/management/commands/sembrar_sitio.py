from django.core.management.base import BaseCommand

from apps.sitio.models import ConfiguracionSitio, PaginaInformativa


PAGINAS_DEFAULT = [
    {
        'slug': 'nosotros',
        'titulo': 'Nosotros',
        'contenido': (
            'Somos una rentadora local comprometida con vehículos en buen estado '
            'y un servicio claro desde la reserva hasta la devolución.\n\n'
            'Edita este texto desde el panel: Sitio web → Páginas.'
        ),
        'orden': 1,
    },
    {
        'slug': 'contacto',
        'titulo': 'Contacto',
        'contenido': (
            'Teléfono y horario se muestran en el pie de página según la configuración de la empresa.\n\n'
            'Puedes añadir aquí instrucciones para llegar a la sucursal o formas de contacto.'
        ),
        'orden': 2,
    },
    {
        'slug': 'servicios',
        'titulo': 'Servicios',
        'contenido': (
            'Alquiler por día, entrega en sucursal, vehículos automáticos y manuales.\n\n'
            'Personaliza esta página con tus servicios reales.'
        ),
        'orden': 3,
    },
]


class Command(BaseCommand):
    help = 'Crea configuración del sitio y páginas informativas por defecto'

    def handle(self, *args, **options):
        ConfiguracionSitio.obtener()
        creadas = 0
        for data in PAGINAS_DEFAULT:
            _, created = PaginaInformativa.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'titulo': data['titulo'],
                    'contenido': data['contenido'],
                    'orden': data['orden'],
                    'publicada': True,
                    'en_menu': True,
                },
            )
            if created:
                creadas += 1
        self.stdout.write(self.style.SUCCESS(
            f'Configuración lista. {creadas} página(s) nueva(s).'
        ))
