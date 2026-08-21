import json
import os
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.sitemaps import Sitemap
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

HOME_PREVIEW_SESSION_KEY = 'sitio_home_preview'
PAGINA_PREVIEW_SESSION_KEY = 'sitio_pagina_preview'
SITIO_PREVIEW_IMAGENES = ('home_fondo_imagen', 'logo', 'favicon')

from apps.configuracion.models import ConfiguracionEmpresa
from apps.core.permisos import es_admin
from apps.core.utils import paginar_queryset
from apps.vehiculos.models import Vehiculo

from .forms import ConfiguracionSitioForm, PaginaInformativaForm, ReservaWebForm
from .i18n import COOKIE_IDIOMA, idioma_actual
from .models import ConfiguracionSitio, PaginaInformativa
from .seo import meta_descripcion_flota, meta_descripcion_home, meta_descripcion_vehiculo
from .services import (
    bloques_mantenimiento_dia,
    demasiados_intentos_reserva,
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
        'favicon_url': sitio.url_favicon(),
        'menu_paginas': paginas,
        'idioma': idioma_actual(request),
    }


def _contexto_home(request, sitio=None):
    ctx = _contexto_publico(request)
    if sitio is not None:
        ctx['sitio'] = sitio
    publicos = vehiculos_publicos()
    ctx['destacados'] = publicos.filter(destacado_web=True)[:6]
    if not ctx['destacados']:
        ctx['destacados'] = publicos[:6]
    ctx['total_vehiculos'] = publicos.count()
    ctx['categorias_flota'] = Vehiculo.Categoria.choices
    ctx['meta_description'] = meta_descripcion_home(ctx['empresa'], ctx['sitio'], ctx['idioma'])
    return ctx


def _serializar_home_preview(form, request, config):
    sitio = form.save(commit=False)
    if form.cleaned_data.get('quitar_home_fondo'):
        sitio.home_fondo_imagen = None
    elif not request.FILES.get('home_fondo_imagen') and config.home_fondo_imagen:
        sitio.home_fondo_imagen = config.home_fondo_imagen

    if request.FILES.get('home_fondo_imagen'):
        uploaded = request.FILES['home_fondo_imagen']
        ext = os.path.splitext(uploaded.name)[1].lower() or '.jpg'
        path = default_storage.save(
            f'sitio/preview/{request.user.pk}/fondo{ext}',
            uploaded,
        )
        sitio.home_fondo_imagen.name = path

    if form.cleaned_data.get('quitar_logo'):
        sitio.logo = None
    elif not request.FILES.get('logo') and config.logo:
        sitio.logo = config.logo

    if request.FILES.get('logo'):
        uploaded = request.FILES['logo']
        ext = os.path.splitext(uploaded.name)[1].lower() or '.png'
        path = default_storage.save(
            f'sitio/preview/{request.user.pk}/logo{ext}',
            uploaded,
        )
        sitio.logo.name = path

    if form.cleaned_data.get('quitar_favicon'):
        sitio.favicon = None
    elif not request.FILES.get('favicon') and config.favicon:
        sitio.favicon = config.favicon

    if request.FILES.get('favicon'):
        uploaded = request.FILES['favicon']
        ext = os.path.splitext(uploaded.name)[1].lower() or '.png'
        path = default_storage.save(
            f'sitio/preview/{request.user.pk}/favicon{ext}',
            uploaded,
        )
        sitio.favicon.name = path

    data = {}
    for field in sitio._meta.fields:
        if field.name == 'id':
            continue
        value = getattr(sitio, field.name)
        if field.name in SITIO_PREVIEW_IMAGENES:
            data[field.name] = value.name if value else ''
        elif isinstance(value, bool):
            data[field.name] = value
        elif value is None:
            data[field.name] = ''
        else:
            data[field.name] = value
    return data


def _sitio_desde_preview(data):
    sitio = ConfiguracionSitio.obtener()
    for field in sitio._meta.fields:
        if field.name in ('id', *SITIO_PREVIEW_IMAGENES):
            continue
        if field.name not in data:
            continue
        setattr(sitio, field.name, field.to_python(data[field.name]))

    for img_field in SITIO_PREVIEW_IMAGENES:
        path = data.get(img_field) or ''
        if path:
            getattr(sitio, img_field).name = path
        else:
            setattr(sitio, img_field, None)
    return sitio


def _serializar_pagina_preview(form, pk=None):
    pagina = form.save(commit=False)
    return {
        'pk': pk,
        'slug': pagina.slug,
        'titulo': pagina.titulo,
        'contenido': pagina.contenido,
        'css_extra': pagina.css_extra or '',
        'js_extra': pagina.js_extra or '',
        'publicada': pagina.publicada,
        'en_menu': pagina.en_menu,
        'orden': pagina.orden,
    }


def _pagina_desde_preview(data):
    pk = data.get('pk')
    if pk:
        pagina = PaginaInformativa.objects.filter(pk=pk).first() or PaginaInformativa()
    else:
        pagina = PaginaInformativa()

    for field in PaginaInformativa._meta.fields:
        if field.name == 'id':
            continue
        if field.name not in data:
            continue
        setattr(pagina, field.name, field.to_python(data[field.name]))
    return pagina


def _url_panel_pagina_preview(preview):
    pk = preview.get('pk')
    if pk:
        return reverse('sitio_web:panel_pagina_editar', kwargs={'pk': pk})
    return reverse('sitio_web:panel_pagina_crear')


@login_not_required
def home(request):
    return render(request, 'sitio/home.html', _contexto_home(request))


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
        'meta_description': meta_descripcion_flota(ctx['empresa'], ctx['idioma']),
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
        'meta_description': meta_descripcion_vehiculo(vehiculo, ctx['empresa'], ctx['idioma']),
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
        if demasiados_intentos_reserva(request):
            ctx.update({
                'form': ReservaWebForm(vehiculo=vehiculo, initial=initial, idioma=ctx['idioma']),
                'vehiculo': vehiculo,
                'error_limite': 'Demasiadas solicitudes. Intenta de nuevo en unos minutos o escríbenos por WhatsApp.',
            })
            return render(request, 'sitio/reservar.html', ctx, status=429)
        form = ReservaWebForm(request.POST, vehiculo=vehiculo, idioma=ctx['idioma'])
        if form.is_valid():
            reserva = form.guardar_reserva()
            config_sitio = ConfiguracionSitio.obtener()
            ctx['reserva'] = reserva
            if ctx['idioma'] == 'en' and config_sitio.mensaje_reserva_exito_en:
                ctx['mensaje'] = config_sitio.mensaje_reserva_exito_en
            else:
                ctx['mensaje'] = config_sitio.mensaje_reserva_exito
            ctx['wa_msg'] = (
                f'Hola, acabo de hacer la reserva #{reserva.pk} del {reserva.vehiculo.nombre_corto} '
                f'({reserva.fecha_inicio.strftime("%d/%m/%Y")} — '
                f'{reserva.fecha_fin.strftime("%d/%m/%Y")}). ¿Me confirman?'
            )
            return render(request, 'sitio/reserva_exito.html', ctx)
    else:
        form = ReservaWebForm(vehiculo=vehiculo, initial=initial, idioma=ctx['idioma'])

    ctx.update({'form': form, 'vehiculo': vehiculo})
    return render(request, 'sitio/reservar.html', ctx)


# ——— Panel ———

CAMPOS_PESTANA_SITIO = {
    'marca': {'logo', 'quitar_logo', 'favicon', 'quitar_favicon', 'mostrar_nombre_junto_logo'},
    'inicio': {
        'home_titulo', 'home_titulo_en', 'home_subtitulo', 'home_subtitulo_en',
        'home_texto', 'home_texto_en', 'horario', 'meta_descripcion', 'meta_descripcion_en',
        'home_diseno', 'home_fondo_imagen', 'quitar_home_fondo', 'home_fondo_opacidad',
        'home_fondo_tamano', 'home_fondo_posicion', 'home_mostrar_panel',
        'home_mostrar_categorias', 'home_mostrar_destacados', 'home_mostrar_cta',
        'home_mostrar_contador', 'home_mostrar_redes_hero',
        'servicio_24h', 'entrega_aeropuertos', 'mostrar_resenas',
        'resena_calificacion', 'resena_cantidad',
    },
    'contacto': {
        'whatsapp', 'whatsapp_mensaje', 'whatsapp_flotante', 'mostrar_whatsapp',
        'instagram', 'mostrar_instagram', 'facebook', 'mostrar_facebook',
        'tiktok', 'mostrar_tiktok', 'youtube', 'mostrar_youtube',
        'twitter', 'mostrar_twitter',
    },
    'reservas': {
        'reserva_auto_confirmar', 'anticipacion_horas', 'bloquear_mantenimiento',
        'mensaje_reserva_exito', 'mensaje_reserva_exito_en',
    },
    'avanzado': {'home_html_extra', 'css_global', 'js_global'},
}


def _pestana_con_errores(form):
    for field in form.errors:
        for pestana, campos in CAMPOS_PESTANA_SITIO.items():
            if field in campos:
                return pestana
    return 'inicio'


def _resumen_sitio(config, paginas):
    publicadas = paginas.filter(publicada=True).count()
    return {
        'logo_ok': bool(config.logo),
        'favicon_ok': bool(config.favicon),
        'whatsapp_ok': config.whatsapp_activo,
        'paginas_publicadas': publicadas,
        'paginas_total': paginas.count(),
        'vehiculos_web': vehiculos_publicos().count(),
        'auto_confirmar': config.reserva_auto_confirmar,
    }


def panel_index(request):
    config = ConfiguracionSitio.obtener()
    paginas = PaginaInformativa.objects.all()
    pestana_activa = 'inicio'
    restringir_avanzado = not es_admin(request.user)

    if request.method == 'POST':
        form = ConfiguracionSitioForm(
            request.POST, request.FILES, instance=config, restringir_avanzado=restringir_avanzado,
        )
        pestana_activa = request.POST.get('pestana_activa', 'inicio')
        if 'vista_previa_home' in request.POST:
            if form.is_valid():
                request.session[HOME_PREVIEW_SESSION_KEY] = _serializar_home_preview(
                    form, request, config,
                )
                request.session.modified = True
                return redirect('sitio_web:panel_vista_previa_home')
            pestana_activa = _pestana_con_errores(form)
        elif 'guardar_sitio' in request.POST and form.is_valid():
            sitio = form.save(commit=False)
            if form.cleaned_data.get('quitar_home_fondo') and config.home_fondo_imagen:
                config.home_fondo_imagen.delete(save=False)
                sitio.home_fondo_imagen = None
            if form.cleaned_data.get('quitar_logo') and config.logo:
                config.logo.delete(save=False)
                sitio.logo = None
            if form.cleaned_data.get('quitar_favicon') and config.favicon:
                config.favicon.delete(save=False)
                sitio.favicon = None
            sitio.save()
            request.session.pop(HOME_PREVIEW_SESSION_KEY, None)
            messages.success(request, 'Configuración del sitio guardada.')
            return redirect(f'{reverse("sitio_web:panel_index")}?tab={pestana_activa}')
        elif 'guardar_sitio' in request.POST:
            pestana_activa = _pestana_con_errores(form)
    else:
        form = ConfiguracionSitioForm(instance=config, restringir_avanzado=restringir_avanzado)
        pestana_activa = request.GET.get('tab', 'inicio')
        if pestana_activa not in (*CAMPOS_PESTANA_SITIO.keys(), 'paginas'):
            pestana_activa = 'inicio'

    return render(request, 'sitio/panel/index.html', {
        'page_title': 'Sitio web',
        'page_subtitle': 'Contenido y políticas de la web pública',
        'form': form,
        'paginas': paginas,
        'url_publica': '/',
        'resumen': _resumen_sitio(config, paginas),
        'pestana_activa': pestana_activa,
    })


def panel_vista_previa_home(request):
    preview = request.session.get(HOME_PREVIEW_SESSION_KEY)
    if not preview:
        messages.info(request, 'Configura el inicio y pulsa «Vista previa» para ver los cambios.')
        return redirect('sitio_web:panel_index')

    ctx = _contexto_home(request, sitio=_sitio_desde_preview(preview))
    ctx.update({
        'es_vista_previa': True,
        'url_panel_sitio': reverse('sitio_web:panel_index'),
    })
    return render(request, 'sitio/home.html', ctx)


def panel_pagina_crear(request):
    restringir_avanzado = not es_admin(request.user)
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST, restringir_avanzado=restringir_avanzado)
        if 'vista_previa_pagina' in request.POST:
            if form.is_valid():
                request.session[PAGINA_PREVIEW_SESSION_KEY] = _serializar_pagina_preview(form)
                request.session.modified = True
                return redirect('sitio_web:panel_vista_previa_pagina')
        elif 'guardar_pagina' in request.POST and form.is_valid():
            form.save()
            request.session.pop(PAGINA_PREVIEW_SESSION_KEY, None)
            messages.success(request, 'Página creada.')
            return redirect('sitio_web:panel_index')
    else:
        form = PaginaInformativaForm(restringir_avanzado=restringir_avanzado)

    return render(request, 'sitio/panel/pagina_form.html', {
        'page_title': 'Nueva página',
        'form': form,
        'accion': 'crear',
    })


def panel_pagina_editar(request, pk):
    pagina_obj = get_object_or_404(PaginaInformativa, pk=pk)
    restringir_avanzado = not es_admin(request.user)
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST, instance=pagina_obj, restringir_avanzado=restringir_avanzado)
        if 'vista_previa_pagina' in request.POST:
            if form.is_valid():
                request.session[PAGINA_PREVIEW_SESSION_KEY] = _serializar_pagina_preview(form, pk=pk)
                request.session.modified = True
                return redirect('sitio_web:panel_vista_previa_pagina')
        elif 'guardar_pagina' in request.POST and form.is_valid():
            form.save()
            request.session.pop(PAGINA_PREVIEW_SESSION_KEY, None)
            messages.success(request, 'Página actualizada.')
            return redirect('sitio_web:panel_index')
    else:
        form = PaginaInformativaForm(instance=pagina_obj, restringir_avanzado=restringir_avanzado)

    return render(request, 'sitio/panel/pagina_form.html', {
        'page_title': 'Editar página',
        'form': form,
        'accion': 'editar',
        'pagina': pagina_obj,
    })


def panel_vista_previa_pagina(request):
    preview = request.session.get(PAGINA_PREVIEW_SESSION_KEY)
    if not preview:
        messages.info(request, 'Edita la página y pulsa «Vista previa» para ver los cambios.')
        return redirect('sitio_web:panel_index')

    ctx = _contexto_publico(request)
    ctx.update({
        'pagina': _pagina_desde_preview(preview),
        'es_vista_previa': True,
        'url_panel_sitio': _url_panel_pagina_preview(preview),
    })
    return render(request, 'sitio/pagina.html', ctx)


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


@login_not_required
def cambiar_idioma(request, codigo):
    destino = request.META.get('HTTP_REFERER') or reverse('sitio:home')
    respuesta = redirect(destino)
    if codigo in ('es', 'en'):
        respuesta.set_cookie(COOKIE_IDIOMA, codigo, max_age=60 * 60 * 24 * 365)
    return respuesta
