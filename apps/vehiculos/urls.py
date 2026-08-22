from django.urls import path

from . import views

app_name = 'vehiculos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('nuevo/', views.crear, name='crear'),
    path('<int:pk>/rentabilidad/', views.rentabilidad, name='rentabilidad'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]
