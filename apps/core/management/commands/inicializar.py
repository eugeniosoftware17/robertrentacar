from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Aplica migraciones y crea el usuario admin inicial'

    def handle(self, *args, **options):
        self.stdout.write('Aplicando migraciones...')
        call_command('migrate', verbosity=0)
        call_command('crear_grupos')
        call_command('crear_admin')
        call_command('sembrar_sitio')
        self.stdout.write(self.style.SUCCESS(
            'Listo. Inicia el servidor con: python manage.py runserver'
        ))
        self.stdout.write('Login: admin / admin123')
