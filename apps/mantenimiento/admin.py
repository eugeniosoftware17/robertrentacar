from django.contrib import admin

from .models import Mantenimiento


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'fecha', 'tipo', 'estado', 'costo')
    list_filter = ('estado', 'tipo', 'fecha')
    search_fields = ('vehiculo__placa', 'vehiculo__marca', 'descripcion')
