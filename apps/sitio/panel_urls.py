from django.urls import path

from . import views

app_name = 'sitio_web'

urlpatterns = [
    path('', views.panel_index, name='panel_index'),
    path('paginas/nueva/', views.panel_pagina_crear, name='panel_pagina_crear'),
    path('paginas/<int:pk>/', views.panel_pagina_editar, name='panel_pagina_editar'),
]
