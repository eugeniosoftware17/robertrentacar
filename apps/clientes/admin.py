from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'documento', 'telefono', 'activo')
    search_fields = ('nombre', 'apellido', 'documento', 'telefono', 'email')
    list_filter = ('activo',)
