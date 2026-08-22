from django.db.models import Q


def filtrar_vehiculos(qs, termino='', letra=''):
    termino = (termino or '').strip()
    letra = (letra or '').strip()[:1]

    if letra:
        qs = qs.filter(
            Q(marca__istartswith=letra)
            | Q(modelo__istartswith=letra)
            | Q(placa__istartswith=letra)
        )

    if termino:
        qs = qs.filter(
            Q(marca__icontains=termino)
            | Q(modelo__icontains=termino)
            | Q(placa__icontains=termino)
            | Q(color__icontains=termino)
            | Q(categoria__nombre__icontains=termino)
            | Q(categoria__slug__icontains=termino)
        )

    return qs
