from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from apps.core.models import AccesoModulo
from apps.core.permisos import (
    GRUPO_DUENO,
    GRUPO_EMPLEADO,
    GRUPO_SISTEMA,
    MODULOS,
    MODULOS_EMPLEADO_DEFAULT,
    MODULOS_SOLO_SISTEMA,
)
from apps.core.sync_permisos import sincronizar_permisos_grupos


class Command(BaseCommand):
    help = 'Crea los grupos del panel y sincroniza permisos por rol'

    def handle(self, *args, **options):
        for nombre in (GRUPO_SISTEMA, GRUPO_DUENO, GRUPO_EMPLEADO):
            _, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre}" creado.'))
            else:
                self.stdout.write(f'Grupo "{nombre}" ya existía.')

        for clave in MODULOS:
            if clave in MODULOS_SOLO_SISTEMA:
                continue
            permitido = clave in MODULOS_EMPLEADO_DEFAULT
            _, creado = AccesoModulo.objects.get_or_create(
                modulo=clave,
                defaults={'permitido': permitido},
            )
            if creado:
                self.stdout.write(f'  Acceso módulo "{MODULOS[clave]}": {"Sí" if permitido else "No"}')

        sincronizar_permisos_grupos()
        self.stdout.write(self.style.SUCCESS('Grupos y permisos del panel sincronizados.'))
