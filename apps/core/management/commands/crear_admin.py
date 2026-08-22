from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from apps.core.permisos import GRUPO_SISTEMA


class Command(BaseCommand):
    help = 'Crea el usuario administrador inicial del panel'

    def handle(self, *args, **options):
        username = 'admin'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe.'))
            return

        user = User.objects.create_superuser(
            username=username,
            email='admin@rentcar.local',
            password='admin123',
        )
        grupo_admin, _ = Group.objects.get_or_create(name=GRUPO_SISTEMA)
        user.groups.add(grupo_admin)
        self.stdout.write(self.style.SUCCESS(
            f'Usuario creado: {username} / admin123 — cámbialo después del primer acceso.'
        ))
