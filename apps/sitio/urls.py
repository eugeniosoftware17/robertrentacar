from django.urls import path

from . import views

app_name = 'sitio'

urlpatterns = [
    path('', views.home, name='home'),
    path('flota/', views.flota, name='flota'),
    path('flota/<slug:slug>/', views.vehiculo_detalle, name='vehiculo'),
    path('flota/<int:pk>/', views.vehiculo_detalle_legacy, name='vehiculo_legacy'),
    path('flota/<slug:slug>/disponibilidad/', views.api_disponibilidad, name='api_disponibilidad'),
    path('pagina/<slug:slug>/', views.pagina, name='pagina'),
    path('reservar/<slug:slug>/', views.reservar, name='reservar'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('idioma/<str:codigo>/', views.cambiar_idioma, name='cambiar_idioma'),
]
