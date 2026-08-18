from django.core.management.base import BaseCommand

from apps.reservas.services import actualizar_estados_reservas, limpiar_videos_entrega_vencidos


class Command(BaseCommand):
    help = 'Actualiza estados de reservas (Activa/Completada) y borra videos de entrega vencidos'

    def handle(self, *args, **options):
        total = actualizar_estados_reservas()
        self.stdout.write(self.style.SUCCESS(f'{total} reserva(s) actualizada(s).'))
        borrados = limpiar_videos_entrega_vencidos()
        self.stdout.write(self.style.SUCCESS(f'{borrados} video(s) de entrega vencido(s) eliminado(s).'))
