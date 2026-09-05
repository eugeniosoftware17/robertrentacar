from django.core.paginator import Paginator


def paginar_queryset(request, queryset, por_pagina=15, per_page=None, param='page'):
    paginator = Paginator(queryset, per_page if per_page is not None else por_pagina)
    return paginator.get_page(request.GET.get(param, 1))
