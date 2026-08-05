from django.db import models
from urllib.parse import quote
import re


class ConfiguracionSitio(models.Model):
    home_titulo = models.CharField('Título del inicio', max_length=160, default='Alquiler de vehículos')
    home_subtitulo = models.CharField('Subtítulo del inicio', max_length=240, blank=True)
    home_texto = models.TextField('Texto del inicio', blank=True)
    whatsapp = models.CharField(
        'WhatsApp (número)',
        max_length=30,
        blank=True,
        help_text='Con código de país, ej. +1 809 555 1234',
    )
    whatsapp_mensaje = models.CharField(
        'Mensaje automático de WhatsApp',
        max_length=300,
        blank=True,
        default='Hola, me interesa alquilar un vehículo. ¿Tienen disponibilidad?',
        help_text='Texto prellenado cuando el cliente abre WhatsApp desde la web.',
    )
    whatsapp_flotante = models.BooleanField(
        'Botón flotante de WhatsApp',
        default=True,
        help_text='Botón verde fijo en la esquina de todas las páginas.',
    )
    mostrar_whatsapp = models.BooleanField('Mostrar WhatsApp', default=True)
    horario = models.CharField('Horario de atención', max_length=200, blank=True)
    instagram = models.URLField('Instagram', blank=True)
    facebook = models.URLField('Facebook', blank=True)
    tiktok = models.URLField('TikTok', blank=True)
    youtube = models.URLField('YouTube', blank=True)
    twitter = models.URLField('X (Twitter)', blank=True)
    mostrar_instagram = models.BooleanField('Mostrar Instagram', default=True)
    mostrar_facebook = models.BooleanField('Mostrar Facebook', default=True)
    mostrar_tiktok = models.BooleanField('Mostrar TikTok', default=False)
    mostrar_youtube = models.BooleanField('Mostrar YouTube', default=False)
    mostrar_twitter = models.BooleanField('Mostrar X (Twitter)', default=False)
    reserva_auto_confirmar = models.BooleanField(
        'Confirmar reservas web automáticamente',
        default=False,
        help_text='Si está desactivado, las reservas web quedan pendientes hasta confirmarlas en el panel.',
    )
    anticipacion_horas = models.PositiveSmallIntegerField(
        'Anticipación mínima (horas)',
        default=24,
    )
    bloquear_mantenimiento = models.BooleanField(
        'Ocultar vehículos en mantenimiento de la web',
        default=True,
    )
    mensaje_reserva_exito = models.TextField(
        'Mensaje tras reservar',
        blank=True,
        default='Gracias. Hemos recibido tu solicitud. Te contactaremos pronto para confirmar.',
    )
    meta_descripcion = models.CharField(
        'Meta descripción (SEO inicio)',
        max_length=160,
        blank=True,
        help_text='Texto para Google (máx. 160 caracteres). Si está vacío se genera automáticamente.',
    )
    home_html_extra = models.TextField(
        'HTML extra del inicio',
        blank=True,
        help_text='Bloque HTML personalizado en la página de inicio (antes del pie de llamada a la acción).',
    )
    css_global = models.TextField(
        'CSS global del sitio',
        blank=True,
        help_text='Estilos aplicados a todas las páginas públicas. Solo administradores.',
    )
    js_global = models.TextField(
        'JavaScript global del sitio',
        blank=True,
        help_text='Scripts en todas las páginas (Analytics, Pixel, etc.). Solo administradores.',
    )

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return 'Configuración del sitio web'

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @staticmethod
    def _limpiar_telefono(numero):
        return re.sub(r'\D', '', numero or '')

    def url_whatsapp(self, mensaje=None):
        numero = self._limpiar_telefono(self.whatsapp)
        if not numero:
            return ''
        texto = self.whatsapp_mensaje if mensaje is None else mensaje
        if texto:
            return f'https://wa.me/{numero}?text={quote(texto.strip())}'
        return f'https://wa.me/{numero}'

    def redes_sociales(self):
        """Redes activas según URL + casilla «mostrar»."""
        items = []
        if self.mostrar_whatsapp and self.whatsapp:
            items.append({
                'red': 'whatsapp',
                'nombre': 'WhatsApp',
                'url': self.url_whatsapp(),
            })
        for red, mostrar, url, nombre in (
            ('instagram', self.mostrar_instagram, self.instagram, 'Instagram'),
            ('facebook', self.mostrar_facebook, self.facebook, 'Facebook'),
            ('tiktok', self.mostrar_tiktok, self.tiktok, 'TikTok'),
            ('youtube', self.mostrar_youtube, self.youtube, 'YouTube'),
            ('twitter', self.mostrar_twitter, self.twitter, 'X'),
        ):
            if mostrar and url:
                items.append({'red': red, 'nombre': nombre, 'url': url})
        return items

    @property
    def tiene_redes(self):
        return bool(self.redes_sociales())

    @property
    def whatsapp_activo(self):
        return self.mostrar_whatsapp and bool(self.whatsapp)


class PaginaInformativa(models.Model):
    class Slug(models.TextChoices):
        NOSOTROS = 'nosotros', 'Nosotros'
        CONTACTO = 'contacto', 'Contacto'
        SERVICIOS = 'servicios', 'Servicios'

    slug = models.SlugField('Identificador', max_length=40, unique=True)
    titulo = models.CharField('Título', max_length=120)
    contenido = models.TextField(
        'Contenido (HTML)',
        help_text='Puedes usar HTML: <h2>, <p>, <img>, <iframe>, listas, etc.',
    )
    css_extra = models.TextField(
        'CSS de la página',
        blank=True,
        help_text='Estilos solo para esta página.',
    )
    js_extra = models.TextField(
        'JavaScript de la página',
        blank=True,
        help_text='Scripts solo para esta página.',
    )
    publicada = models.BooleanField('Publicada', default=True)
    en_menu = models.BooleanField('Mostrar en menú', default=True)
    orden = models.PositiveSmallIntegerField('Orden en menú', default=0)

    class Meta:
        ordering = ['orden', 'titulo']
        verbose_name = 'Página informativa'
        verbose_name_plural = 'Páginas informativas'

    def __str__(self):
        return self.titulo
