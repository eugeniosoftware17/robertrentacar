from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.vehiculos.models import Vehiculo


def crear_vehiculo(placa, **extra):
    defaults = {
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'anio': 2022,
        'placa': placa,
        'tarifa_diaria': Decimal('2000.00'),
        'activo': True,
    }
    defaults.update(extra)
    return Vehiculo.objects.create(**defaults)


class DashboardAlertasSeguroTests(TestCase):
    """El recordatorio de seguro no debe perderse detrás de otras alertas."""

    def setUp(self):
        self.hoy = timezone.localdate()
        self.admin = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='clave-segura-123',
        )
        self.client.force_login(self.admin)

    def test_seguro_vencido_genera_alerta_urgente(self):
        crear_vehiculo('SEG0001', seguro_vence=self.hoy - timedelta(days=5))
        respuesta = self.client.get(reverse('dashboard'))
        alertas = respuesta.context['alertas']
        self.assertTrue(any('Seguro vencido' in a['detalle'] for a in alertas))
        alerta_seguro = next(a for a in alertas if 'Seguro vencido' in a['detalle'])
        self.assertEqual(alerta_seguro['tipo'], 'Urgente')

    def test_alerta_de_seguro_no_se_pierde_con_varios_vehiculos_en_mantenimiento(self):
        for i in range(4):
            crear_vehiculo(f'MNT000{i}', estado=Vehiculo.Estado.MANTENIMIENTO)
        crear_vehiculo('SEG0002', seguro_vence=self.hoy + timedelta(days=10))

        respuesta = self.client.get(reverse('dashboard'))
        alertas = respuesta.context['alertas']
        self.assertTrue(any('Seguro vence' in a['detalle'] for a in alertas))

    def test_seguro_por_vencer_pronto_genera_aviso(self):
        crear_vehiculo('SEG0003', seguro_vence=self.hoy + timedelta(days=15))
        respuesta = self.client.get(reverse('dashboard'))
        alertas = respuesta.context['alertas']
        alerta_seguro = next(a for a in alertas if 'Seguro vence' in a['detalle'])
        self.assertEqual(alerta_seguro['tipo'], 'Aviso')

    def test_seguro_lejano_no_genera_alerta(self):
        crear_vehiculo('SEG0004', seguro_vence=self.hoy + timedelta(days=90))
        respuesta = self.client.get(reverse('dashboard'))
        alertas = respuesta.context['alertas']
        self.assertFalse(any('Seguro' in a['detalle'] for a in alertas))
