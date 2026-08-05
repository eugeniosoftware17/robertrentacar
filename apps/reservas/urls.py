from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('contratos/', views.lista_contratos, name='contratos'),
    path('nueva/', views.crear, name='crear'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/entrega/', views.entrega, name='entrega'),
    path('<int:pk>/devolucion/', views.devolucion, name='devolucion'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    path('<int:pk>/contrato/', views.contrato, name='contrato'),
]
