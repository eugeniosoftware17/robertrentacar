from django.urls import path

from . import views

app_name = 'configuracion'

urlpatterns = [
    path('', views.index, name='index'),
    path('contrato-demo/', views.contrato_demo, name='contrato_demo'),
]
