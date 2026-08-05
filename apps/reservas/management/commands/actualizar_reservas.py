from django.core.management.base import BaseCommand

from apps.reservas.services import actualizar_estados_reservas


class Command(BaseCommand):
    help = 'Actualiza estados de reservas (Activa/Completada) según las fechas'

    def handle(self, *args, **options):
        total = actualizar_estados_reservas()
        self.stdout.write(self.style.SUCCESS(f'{total} reserva(s) actualizada(s).'))
