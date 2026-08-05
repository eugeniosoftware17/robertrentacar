from django.core.paginator import Paginator


def paginar_queryset(request, queryset, por_pagina=15, param='page'):
    paginator = Paginator(queryset, por_pagina)
    return paginator.get_page(request.GET.get(param, 1))
