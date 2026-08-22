from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from apps.core.sync_permisos import permisos_panel


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Acceso al panel'), {
            'fields': ('is_active', 'is_staff'),
            'description': (
                'Marque «Personal de staff» solo si este usuario debe entrar al Admin Django. '
                'NO marque «Superusuario» para empleados normales.'
            ),
        }),
        (_('Roles y permisos del panel'), {
            'fields': ('groups', 'user_permissions'),
            'description': (
                'Forma recomendada: asigne «Empleado», «Dueño del negocio» o «Administrador del sistema». '
                'Configuración, Sitio web y Admin Django son solo para el administrador del sistema (superusuario). '
                'También puede elegir permisos individuales del panel (Acceder a Reservas, etc.) '
                'en la lista de abajo — esos SÍ controlan qué ve el usuario en el menú.'
            ),
        }),
        (_('Superusuario'), {
            'fields': ('is_superuser',),
            'description': 'Solo para el dueño del sistema. Un superusuario ve todo sin restricciones.',
            'classes': ('collapse',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'groups'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            kwargs['queryset'] = permisos_panel()
            kwargs['help_text'] = (
                'Permisos del panel Rent Car. Elija los módulos que este usuario puede ver.'
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class GroupAdmin(BaseGroupAdmin):
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'permissions':
            kwargs['queryset'] = permisos_panel()
            kwargs['help_text'] = (
                'Permisos del panel Rent Car. Los grupos se sincronizan desde Configuración del panel '
                'o con el comando crear_grupos.'
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
