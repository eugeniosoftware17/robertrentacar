from decimal import Decimal
from urllib.parse import quote
import re

from django.db import models


class ConfiguracionSitio(models.Model):
    class HomeDiseno(models.TextChoices):
        CLASICO = 'clasico', 'Clásico — texto + panel lateral'
        FOTO = 'foto', 'Foto de fondo — hero amplio con imagen'
        CENTRADO = 'centrado', 'Centrado — texto al medio'
        COMPACTO = 'compacto', 'Compacto — hero más pequeño'
        SPLIT = 'split', 'Dividido — imagen a un lado'

    class FondoPosicion(models.TextChoices):
        ARRIBA_IZQUIERDA = 'left top', 'Arriba izquierda'
        ARRIBA = 'top', 'Arriba centro'
        ARRIBA_DERECHA = 'right top', 'Arriba derecha'
        IZQUIERDA = 'left', 'Centro izquierda'
        CENTRO = 'center', 'Centro'
        DERECHA = 'right', 'Centro derecha'
        ABAJO_IZQUIERDA = 'left bottom', 'Abajo izquierda'
        ABAJO = 'bottom', 'Abajo centro'
        ABAJO_DERECHA = 'right bottom', 'Abajo derecha'

    class FondoTamano(models.TextChoices):
        CUBRIR = 'cover', 'Cubrir — llena el espacio (puede recortar bordes)'
        AJUSTAR = 'contain', 'Ajustar — se ve completa (puede dejar franjas)'

    home_titulo = models.CharField('Título del inicio', max_length=160, default='Alquiler de vehículos')
    home_titulo_en = models.CharField(
        'Título del inicio (inglés)', max_length=160, blank=True,
        help_text='Si lo dejas vacío, se usa el texto en español para los visitantes en inglés.',
    )
    home_subtitulo = models.CharField('Subtítulo del inicio', max_length=240, blank=True)
    home_subtitulo_en = models.CharField('Subtítulo del inicio (inglés)', max_length=240, blank=True)
    home_texto = models.TextField('Texto del inicio', blank=True)
    home_texto_en = models.TextField('Texto del inicio (inglés)', blank=True)
    home_diseno = models.CharField(
        'Diseño del inicio',
        max_length=20,
        choices=HomeDiseno.choices,
        default=HomeDiseno.CLASICO,
    )
    home_fondo_imagen = models.ImageField(
        'Imagen de fondo del inicio',
        upload_to='sitio/home/',
        blank=True,
        null=True,
        help_text='Recomendado: 1920×900 px o similar. JPG o WebP.',
    )
    home_fondo_opacidad = models.PositiveSmallIntegerField(
        'Oscurecer foto (%)',
        default=60,
        help_text='0 = sin oscurecer, 100 = muy oscuro. Mejora la lectura del texto.',
    )
    home_fondo_posicion = models.CharField(
        'Posición de la foto',
        max_length=20,
        choices=FondoPosicion.choices,
        default=FondoPosicion.CENTRO,
        help_text='Qué parte de la imagen se mantiene visible en pantallas angostas.',
    )
    home_fondo_tamano = models.CharField(
        'Tamaño de la foto',
        max_length=10,
        choices=FondoTamano.choices,
        default=FondoTamano.CUBRIR,
    )
    home_mostrar_panel = models.BooleanField('Panel «¿Por qué reservar?»', default=True)
    home_mostrar_categorias = models.BooleanField('Sección categorías', default=True)
    home_mostrar_destacados = models.BooleanField('Vehículos destacados', default=True)
    home_mostrar_cta = models.BooleanField('Llamada a la acción final', default=True)
    home_mostrar_contador = models.BooleanField('Contador de vehículos', default=True)
    home_mostrar_redes_hero = models.BooleanField('Redes sociales en el hero', default=True)
    servicio_24h = models.BooleanField('Atención 24 horas', default=False)
    entrega_aeropuertos = models.BooleanField('Entrega en aeropuertos de RD', default=False)
    mostrar_resenas = models.BooleanField('Mostrar calificación de reseñas', default=False)
    resena_calificacion = models.DecimalField(
        'Calificación (de 5)', max_digits=2, decimal_places=1, default=Decimal('5.0'),
    )
    resena_cantidad = models.PositiveIntegerField('Cantidad de reseñas', default=0)
    logo = models.ImageField(
        'Logo del sitio',
        upload_to='sitio/logo/',
        blank=True,
        null=True,
        help_text='PNG con fondo transparente recomendado. Altura ideal: 40–56 px.',
    )
    favicon = models.FileField(
        'Icono del navegador (favicon)',
        upload_to='sitio/favicon/',
        blank=True,
        null=True,
        help_text='PNG, ICO o WebP cuadrado. Recomendado: 32×32 o 192×192 px.',
    )
    mostrar_nombre_junto_logo = models.BooleanField(
        'Mostrar nombre junto al logo',
        default=True,
        help_text='Si desactivas, solo se verá la imagen del logo en el encabezado.',
    )
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
    mensaje_reserva_exito_en = models.TextField('Mensaje tras reservar (inglés)', blank=True)
    meta_descripcion = models.CharField(
        'Meta descripción (SEO inicio)',
        max_length=160,
        blank=True,
        help_text='Texto para Google (máx. 160 caracteres). Si está vacío se genera automáticamente.',
    )
    meta_descripcion_en = models.CharField(
        'Meta descripción (SEO inicio, inglés)', max_length=160, blank=True,
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

    @property
    def home_tiene_fondo(self):
        return bool(self.home_fondo_imagen)

    @property
    def tiene_logo(self):
        return bool(self.logo)

    @property
    def tiene_favicon(self):
        return bool(self.favicon)

    def url_favicon(self):
        if self.favicon:
            return self.favicon.url
        if self.logo:
            return self.logo.url
        return None


class PaginaInformativa(models.Model):
    class Slug(models.TextChoices):
        NOSOTROS = 'nosotros', 'Nosotros'
        CONTACTO = 'contacto', 'Contacto'
        SERVICIOS = 'servicios', 'Servicios'

    slug = models.SlugField('Identificador', max_length=40, unique=True)
    titulo = models.CharField('Título', max_length=120)
    titulo_en = models.CharField(
        'Título (inglés)', max_length=120, blank=True,
        help_text='Si lo dejas vacío, se usa el título en español para los visitantes en inglés.',
    )
    contenido = models.TextField(
        'Contenido (HTML)',
        help_text='Puedes usar HTML: <h2>, <p>, <img>, <iframe>, listas, etc.',
    )
    contenido_en = models.TextField(
        'Contenido (HTML, inglés)',
        blank=True,
        help_text='Si lo dejas vacío, se usa el contenido en español para los visitantes en inglés.',
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
