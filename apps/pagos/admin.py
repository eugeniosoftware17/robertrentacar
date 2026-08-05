from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'monto', 'tipo', 'metodo', 'fecha')
    list_filter = ('tipo', 'metodo', 'fecha')
    search_fields = ('reserva__cliente__nombre', 'referencia')
