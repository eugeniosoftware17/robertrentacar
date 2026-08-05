from django import template

register = template.Library()


@register.simple_tag
def whatsapp_url(sitio, mensaje=None):
    return sitio.url_whatsapp(mensaje=mensaje)
