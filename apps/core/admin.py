from django.contrib import admin

from .models import AccesoModulo


@admin.register(AccesoModulo)
class AccesoModuloAdmin(admin.ModelAdmin):
    list_display = ('modulo', 'permitido')
    list_editable = ('permitido',)
