from .i18n import idioma_actual


def idioma_publico(request):
    return {'idioma_actual': idioma_actual(request)}
