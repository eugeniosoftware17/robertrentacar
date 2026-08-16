from django.urls import path

from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.index, name='index'),

    path('empleados/', views.empleados_lista, name='empleados_lista'),
    path('empleados/nuevo/', views.empleado_crear, name='empleado_crear'),
    path('empleados/<int:pk>/editar/', views.empleado_editar, name='empleado_editar'),
    path('empleados/<int:pk>/eliminar/', views.empleado_eliminar, name='empleado_eliminar'),

    path('nomina/', views.nomina_lista, name='nomina_lista'),
    path('nomina/nuevo/', views.nomina_crear, name='nomina_crear'),
    path('nomina/<int:pk>/editar/', views.nomina_editar, name='nomina_editar'),
    path('nomina/<int:pk>/eliminar/', views.nomina_eliminar, name='nomina_eliminar'),

    path('gastos/', views.gastos_lista, name='gastos_lista'),
    path('gastos/nuevo/', views.gasto_crear, name='gasto_crear'),
    path('gastos/<int:pk>/editar/', views.gasto_editar, name='gasto_editar'),
    path('gastos/<int:pk>/eliminar/', views.gasto_eliminar, name='gasto_eliminar'),
]
