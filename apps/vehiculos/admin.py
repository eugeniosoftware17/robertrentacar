from django.contrib import admin

from .models import CategoriaVehiculo, Vehiculo


@admin.register(CategoriaVehiculo)
class CategoriaVehiculoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activa', 'orden')
    list_editable = ('activa', 'orden')
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'anio', 'placa', 'categoria', 'estado', 'tarifa_diaria', 'activo')
    search_fields = ('marca', 'modelo', 'placa')
    list_filter = ('estado', 'categoria', 'activo')
