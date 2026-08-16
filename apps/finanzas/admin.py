from django.contrib import admin

from .models import Empleado, Gasto, PagoNomina


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'puesto', 'salario_base', 'activo')
    list_filter = ('activo', 'puesto')
    search_fields = ('nombre', 'apellido', 'puesto')


@admin.register(PagoNomina)
class PagoNominaAdmin(admin.ModelAdmin):
    list_display = ('id', 'empleado', 'concepto', 'monto', 'fecha_pago', 'metodo')
    list_filter = ('concepto', 'metodo', 'fecha_pago')
    search_fields = ('empleado__nombre', 'empleado__apellido')


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id', 'concepto', 'categoria', 'monto', 'fecha', 'vehiculo')
    list_filter = ('categoria', 'fecha')
    search_fields = ('concepto', 'vehiculo__placa')
