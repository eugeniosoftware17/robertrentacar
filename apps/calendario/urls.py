from django.urls import path

from . import views

app_name = 'calendario'

urlpatterns = [
    path('', views.index, name='index'),
]
