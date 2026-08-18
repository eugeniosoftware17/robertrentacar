from django import template

from apps.sitio.i18n import IDIOMA_DEFECTO, texto, texto_categoria, texto_transmision

register = template.Library()


@register.simple_tag
def whatsapp_url(sitio, mensaje=None):
    return sitio.url_whatsapp(mensaje=mensaje)


@register.simple_tag(takes_context=True)
def t(context, clave, **kwargs):
    idioma = context.get('idioma_actual', IDIOMA_DEFECTO)
    return texto(clave, idioma, **kwargs)


@register.simple_tag(takes_context=True)
def t_categoria(context, valor):
    idioma = context.get('idioma_actual', IDIOMA_DEFECTO)
    return texto_categoria(valor, idioma)


@register.simple_tag(takes_context=True)
def t_transmision(context, valor):
    idioma = context.get('idioma_actual', IDIOMA_DEFECTO)
    return texto_transmision(valor, idioma)


@register.simple_tag(takes_context=True)
def campo(context, obj, nombre):
    """Devuelve el campo `<nombre>_en` del objeto si el idioma es inglés y
    tiene contenido; si no, cae al campo en español `<nombre>`."""
    idioma = context.get('idioma_actual', IDIOMA_DEFECTO)
    valor_es = getattr(obj, nombre, '') or ''
    if idioma == 'en':
        valor_en = getattr(obj, f'{nombre}_en', '') or ''
        if valor_en:
            return valor_en
    return valor_es
