from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def sincronizar_permisos_tras_migrar(sender, **kwargs):
    if sender.name != 'apps.core':
        return
    from .sync_permisos import sincronizar_permisos_grupos

    sincronizar_permisos_grupos()
