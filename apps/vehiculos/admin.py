from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'anio', 'placa', 'estado', 'tarifa_diaria', 'activo')
    search_fields = ('marca', 'modelo', 'placa')
    list_filter = ('estado', 'categoria', 'activo')
