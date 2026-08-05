from django.contrib import admin

from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'vehiculo', 'fecha_inicio', 'fecha_fin', 'estado', 'precio_total')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'vehiculo__placa')
    list_filter = ('estado', 'fecha_inicio')
