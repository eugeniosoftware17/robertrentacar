from django.db import models

from .permisos import MODULOS


class AccesoModulo(models.Model):
    modulo = models.CharField(
        'Módulo',
        max_length=30,
        choices=[(k, v) for k, v in MODULOS.items()],
        unique=True,
    )
    permitido = models.BooleanField('Permitido para empleados', default=True)

    class Meta:
        verbose_name = 'Acceso de empleado'
        verbose_name_plural = 'Accesos de empleados'
        ordering = ['modulo']
        permissions = [
            ('modulo_dashboard', 'Acceder al Dashboard'),
            ('modulo_calendario', 'Acceder al Calendario'),
            ('modulo_vehiculos', 'Acceder a Vehículos'),
            ('modulo_mantenimiento', 'Acceder a Mantenimiento'),
            ('modulo_reservas', 'Acceder a Reservas'),
            ('modulo_clientes', 'Acceder a Clientes'),
            ('modulo_pagos', 'Acceder a Pagos'),
            ('modulo_reportes', 'Acceder a Reportes'),
            ('modulo_configuracion', 'Acceder a Configuración'),
            ('modulo_sitio_web', 'Acceder al Sitio web'),
            ('modulo_finanzas', 'Acceder a Finanzas'),
        ]

    def __str__(self):
        estado = 'Sí' if self.permitido else 'No'
        return f'{self.get_modulo_display()} — {estado}'
