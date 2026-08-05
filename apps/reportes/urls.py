from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.index, name='index'),
    path('ingresos/', views.ingresos, name='ingresos'),
    path('ocupacion/', views.ocupacion, name='ocupacion'),
]
