from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve

from apps.core import views as core_views

_panel = settings.PANEL_PATH.strip('/') + '/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.cuentas.urls')),
    path('', include('apps.sitio.urls')),
    path(_panel, include([
        path('', core_views.dashboard, name='dashboard'),
        path('vehiculos/', include('apps.vehiculos.urls')),
        path('clientes/', include('apps.clientes.urls')),
        path('reservas/', include('apps.reservas.urls')),
        path('calendario/', include('apps.calendario.urls')),
        path('mantenimiento/', include('apps.mantenimiento.urls')),
        path('pagos/', include('apps.pagos.urls')),
        path('reportes/', include('apps.reportes.urls')),
        path('finanzas/', include('apps.finanzas.urls')),
        path('configuracion/', include('apps.configuracion.urls')),
        path('sitio/', include('apps.sitio.panel_urls')),
    ])),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
