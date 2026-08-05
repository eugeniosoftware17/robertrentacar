from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from apps.core.models import AccesoModulo
from apps.core.permisos import GRUPO_ADMIN, GRUPO_EMPLEADO, MODULOS, MODULOS_EMPLEADO_DEFAULT
from apps.core.sync_permisos import sincronizar_permisos_grupos


class Command(BaseCommand):
    help = 'Crea los grupos Administrador y Empleado, y sincroniza permisos del panel'

    def handle(self, *args, **options):
        admin, creado_admin = Group.objects.get_or_create(name=GRUPO_ADMIN)
        empleado, creado_empleado = Group.objects.get_or_create(name=GRUPO_EMPLEADO)

        if creado_admin:
            self.stdout.write(self.style.SUCCESS(f'Grupo "{GRUPO_ADMIN}" creado.'))
        else:
            self.stdout.write(f'Grupo "{GRUPO_ADMIN}" ya existía.')

        if creado_empleado:
            self.stdout.write(self.style.SUCCESS(f'Grupo "{GRUPO_EMPLEADO}" creado.'))
        else:
            self.stdout.write(f'Grupo "{GRUPO_EMPLEADO}" ya existía.')

        for clave in MODULOS:
            permitido = clave in MODULOS_EMPLEADO_DEFAULT
            _, creado = AccesoModulo.objects.get_or_create(
                modulo=clave,
                defaults={'permitido': permitido},
            )
            if creado:
                self.stdout.write(f'  Acceso módulo "{MODULOS[clave]}": {"Sí" if permitido else "No"}')

        sincronizar_permisos_grupos()
        self.stdout.write(self.style.SUCCESS('Grupos y permisos del panel sincronizados.'))
