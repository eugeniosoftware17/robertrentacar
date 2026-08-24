from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import PaginaInformativa
from .services import vehiculos_publicos

PAGINAS_INFORMATIVAS = ('nosotros', 'contacto', 'servicios')


class SitioEstaticoSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        items = ['home', 'flota']
        publicadas = set(
            PaginaInformativa.objects.filter(
                slug__in=PAGINAS_INFORMATIVAS,
                publicada=True,
            ).values_list('slug', flat=True)
        )
        items.extend(slug for slug in PAGINAS_INFORMATIVAS if slug in publicadas)
        return items

    def location(self, item):
        if item in ('home', 'flota'):
            return reverse(f'sitio:{item}')
        return reverse('sitio:pagina', kwargs={'slug': item})


class VehiculoSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return vehiculos_publicos()

    def lastmod(self, obj):
        return obj.creado_en

    def location(self, obj):
        return obj.get_absolute_url()
