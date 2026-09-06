import os

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """Resuelve URLs de {% static %}/MEDIA a rutas de archivo reales.

    xhtml2pdf no puede descargar por HTTP el logo ni el CSS: necesita
    la ruta del archivo en disco.
    """
    if uri.startswith(settings.STATIC_URL):
        ruta_relativa = uri.replace(settings.STATIC_URL, '', 1)
        candidatos = [os.path.join(settings.STATIC_ROOT, ruta_relativa)]
        for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
            candidatos.append(os.path.join(static_dir, ruta_relativa))
        for candidato in candidatos:
            if os.path.isfile(candidato):
                return candidato
        return uri
    if uri.startswith(settings.MEDIA_URL):
        ruta_relativa = uri.replace(settings.MEDIA_URL, '', 1)
        return os.path.join(settings.MEDIA_ROOT, ruta_relativa)
    return uri


def render_pdf(template_name, context, filename):
    html = render_to_string(template_name, context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('No se pudo generar el PDF del contrato.', status=500)
    return response
