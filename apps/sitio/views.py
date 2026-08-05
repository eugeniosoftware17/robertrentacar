import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.configuracion.models import ConfiguracionEmpresa
from apps.core.utils import paginar_queryset
from apps.vehiculos.models import Vehiculo

from .forms import ConfiguracionSitioForm, PaginaInformativaForm, ReservaWebForm
from .models import ConfiguracionSitio, PaginaInformativa
from .seo import meta_descripcion_flota, meta_descripcion_home, meta_descripcion_vehiculo
from .services import (
    bloques_mantenimiento_dia,
    fechas_ocupadas,
    filtrar_por_disponibilidad,
    vehiculo_reservable,
    vehiculos_publicos,
    vehiculos_relacionados,
)


def _contexto_publico(request):
    empresa = ConfiguracionEmpresa.obtener()
    sitio = ConfiguracionSitio.obtener()
    paginas = PaginaInformativa.objects.filter(publicada=True, en_menu=True)
    return {
        'empresa': empresa,
        'sitio': sitio,
        'menu_paginas': paginas,
    }


@login_not_required
def home(request):
    ctx = _contexto_publico(request)
    publicos = vehiculos_publicos()
    ctx['destacados'] = publicos.filter(destacado_web=True)[:6]
    if not ctx['destacados']:
        ctx['destacados'] = publicos[:6]
    ctx['total_vehiculos'] = publicos.count()
    ctx['categorias_flota'] = Vehiculo.Categoria.choices
    ctx['meta_description'] = meta_descripcion_home(ctx['empresa'], ctx['sitio'])
    return render(request, 'sitio/home.html', ctx)


@login_not_required
def flota(request):
    ctx = _contexto_publico(request)
    qs = vehiculos_publicos()

    categoria = request.GET.get('categoria', '')
    transmision = request.GET.get('transmision', '')
    fecha_inicio = request.GET.get('desde', '')
    fecha_fin = request.GET.get('hasta', '')

    if categoria:
        qs = qs.filter(categoria=categoria)
    if transmision:
        qs = qs.filter(transmision=transmision)

    fi = ff = None
    try:
        if fecha_inicio:
            fi = date.fromisoformat(fecha_inicio)
        if fecha_fin:
            ff = date.fromisoformat(fecha_fin)
    except ValueError:
        fi = ff = None

    if fi and ff:
        qs = filtrar_por_disponibilidad(qs, fi, ff)

    page_obj = paginar_queryset(request, qs, por_pagina=12)
    ctx.update({
        'page_title': 'Flota',
        'vehiculos': page_obj,
        'page_obj': page_obj,
        'categoria_filtro': categoria,
        'transmision_filtro': transmision,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'categorias': Vehiculo.Categoria.choices,
        'transmisiones': Vehiculo.Transmision.choices,
        'meta_description': meta_descripcion_flota(ctx['empresa']),
    })
    return render(request, 'sitio/flota.html', ctx)


@login_not_required
def vehiculo_detalle(request, slug):
    ctx = _contexto_publico(request)
    vehiculo = get_object_or_404(Vehiculo, slug=slug)
    if not vehiculo_reservable(vehiculo):
        return render(request, 'sitio/no_disponible.html', ctx, status=404)

    hoy = timezone.localdate()
    hasta = hoy + timedelta(days=365)
    tarifa = vehiculo.tarifa_diaria
    ctx.update({
        'vehiculo': vehiculo,
        'ocupadas_json': json.dumps(fechas_ocupadas(vehiculo, hoy, hasta)),
        'mantenimiento_json': json.dumps(bloques_mantenimiento_dia(vehiculo, hoy, hasta)),
        'fecha_min': hoy.isoformat(),
        'relacionados': vehiculos_relacionados(vehiculo),
        'tarifa_semanal': tarifa * 7,
        'tarifa_mensual': tarifa * 30,
        'meta_description': meta_descripcion_vehiculo(vehiculo, ctx['empresa']),
        'wa_msg': (
            f'Hola, me interesa alquilar el {vehiculo.nombre_corto} '
            f'(Ref. {vehiculo.placa}). ¿Está disponible?'
        ),
    })
    return render(request, 'sitio/vehiculo_detalle.html', ctx)


@login_not_required
def vehiculo_detalle_legacy(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    return redirect('sitio:vehiculo', slug=vehiculo.slug, permanent=True)


@login_not_required
@require_GET
def api_disponibilidad(request, slug):
    vehiculo = get_object_or_404(Vehiculo, slug=slug)
    if not vehiculo_reservable(vehiculo):
        return JsonResponse({'error': 'no_publicado'}, status=404)

    try:
        anio = int(request.GET.get('anio', timezone.localdate().year))
        mes = int(request.GET.get('mes', timezone.localdate().month))
        primer = date(anio, mes, 1)
        if mes == 12:
            ultimo = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo = date(anio, mes + 1, 1) - timedelta(days=1)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'mes_invalido'}, status=400)

    return JsonResponse({
        'ocupadas': fechas_ocupadas(vehiculo, primer, ultimo),
        'mantenimiento': bloques_mantenimiento_dia(vehiculo, primer, ultimo),
    })


@login_not_required
def pagina(request, slug):
    ctx = _contexto_publico(request)
    pagina_obj = get_object_or_404(PaginaInformativa, slug=slug, publicada=True)
    ctx['pagina'] = pagina_obj
    return render(request, 'sitio/pagina.html', ctx)


@login_not_required
def reservar(request, slug):
    ctx = _contexto_publico(request)
    vehiculo = get_object_or_404(Vehiculo, slug=slug)
    if not vehiculo_reservable(vehiculo):
        return redirect('sitio:flota')

    initial = {
        'fecha_inicio': request.GET.get('desde', ''),
        'fecha_fin': request.GET.get('hasta', ''),
    }

    if request.method == 'POST':
        form = ReservaWebForm(request.POST, vehiculo=vehiculo)
        if form.is_valid():
            reserva = form.guardar_reserva()
            ctx['reserva'] = reserva
            ctx['mensaje'] = ConfiguracionSitio.obtener().mensaje_reserva_exito
            ctx['wa_msg'] = (
                f'Hola, acabo de hacer la reserva #{reserva.pk} del {reserva.vehiculo.nombre_corto} '
                f'({reserva.fecha_inicio.strftime("%d/%m/%Y")} — '
                f'{reserva.fecha_fin.strftime("%d/%m/%Y")}). ¿Me confirman?'
            )
            return render(request, 'sitio/reserva_exito.html', ctx)
    else:
        form = ReservaWebForm(vehiculo=vehiculo, initial=initial)

    ctx.update({'form': form, 'vehiculo': vehiculo})
    return render(request, 'sitio/reservar.html', ctx)


# ——— Panel ———

def panel_index(request):
    config = ConfiguracionSitio.obtener()
    paginas = PaginaInformativa.objects.all()

    if request.method == 'POST' and 'guardar_sitio' in request.POST:
        form = ConfiguracionSitioForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración del sitio guardada.')
            return redirect('sitio_web:panel_index')
    else:
        form = ConfiguracionSitioForm(instance=config)

    return render(request, 'sitio/panel/index.html', {
        'page_title': 'Sitio web',
        'page_subtitle': 'Contenido y políticas de la web pública',
        'form': form,
        'paginas': paginas,
        'url_publica': '/',
    })


def panel_pagina_crear(request):
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Página creada.')
            return redirect('sitio_web:panel_index')
    else:
        form = PaginaInformativaForm()

    return render(request, 'sitio/panel/pagina_form.html', {
        'page_title': 'Nueva página',
        'form': form,
        'accion': 'crear',
    })


def panel_pagina_editar(request, pk):
    pagina_obj = get_object_or_404(PaginaInformativa, pk=pk)
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST, instance=pagina_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Página actualizada.')
            return redirect('sitio_web:panel_index')
    else:
        form = PaginaInformativaForm(instance=pagina_obj)

    return render(request, 'sitio/panel/pagina_form.html', {
        'page_title': 'Editar página',
        'form': form,
        'accion': 'editar',
        'pagina': pagina_obj,
    })


class VehiculoPublicoSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return vehiculos_publicos()

    def lastmod(self, obj):
        return obj.creado_en

    def location(self, obj):
        return obj.get_absolute_url()


class PaginaSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return PaginaInformativa.objects.filter(publicada=True)

    def location(self, obj):
        return reverse('sitio:pagina', kwargs={'slug': obj.slug})


class SitioEstaticoSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'flota']

    def location(self, item):
        return reverse(f'sitio:{item}')


@login_not_required
def sitemap_xml(request):
    from django.contrib.sitemaps.views import sitemap

    sitemaps = {
        'static': SitioEstaticoSitemap,
        'vehiculos': VehiculoPublicoSitemap,
        'paginas': PaginaSitemap,
    }
    return sitemap(request, sitemaps)


@login_not_required
def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {request.build_absolute_uri(reverse("sitio:sitemap"))}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
