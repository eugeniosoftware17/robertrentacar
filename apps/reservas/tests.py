from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.vehiculos.models import CategoriaVehiculo, Vehiculo

from .models import Reserva
from .services import actualizar_estado_vehiculo, limpiar_videos_entrega_vencidos


def crear_cliente(documento='001-0000001-1', licencia_vence=None):
    hoy = timezone.localdate()
    return Cliente.objects.create(
        nombre='Juan',
        apellido='Pérez',
        documento=documento,
        telefono='809-555-0000',
        licencia_numero='L-1',
        licencia_vence=licencia_vence or hoy + timedelta(days=365),
    )


def crear_vehiculo(placa='A123456', tarifa=Decimal('2000.00'), **extra):
    defaults = {
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'anio': 2022,
        'placa': placa,
        'tarifa_diaria': tarifa,
        'categoria': CategoriaVehiculo.obtener_o_crear_default(),
    }
    defaults.update(extra)
    return Vehiculo.objects.create(**defaults)


class ReservaValidacionTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.cliente = crear_cliente()
        self.vehiculo = crear_vehiculo()

    def test_fecha_fin_anterior_a_inicio_es_invalida(self):
        reserva = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=5),
            fecha_fin=self.hoy + timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_licencia_vencida_bloquea_reserva(self):
        cliente_vencido = crear_cliente(
            documento='001-0000002-2',
            licencia_vence=self.hoy - timedelta(days=1),
        )
        reserva = Reserva(
            cliente=cliente_vencido,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=3),
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_vehiculo_en_mantenimiento_bloquea_reserva(self):
        self.vehiculo.estado = Vehiculo.Estado.MANTENIMIENTO
        self.vehiculo.save(update_fields=['estado'])
        reserva = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=3),
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_seguro_vencido_antes_del_inicio_bloquea_reserva(self):
        self.vehiculo.seguro_vence = self.hoy
        self.vehiculo.save(update_fields=['seguro_vence'])
        reserva = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=5),
            fecha_fin=self.hoy + timedelta(days=7),
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_fechas_solapadas_bloquean_nueva_reserva(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=5),
        )
        conflicto = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=3),
            fecha_fin=self.hoy + timedelta(days=8),
        )
        with self.assertRaises(ValidationError):
            conflicto.full_clean()

    def test_fechas_no_solapadas_no_bloquean(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=5),
        )
        libre = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=6),
            fecha_fin=self.hoy + timedelta(days=8),
        )
        libre.full_clean()  # no debe levantar ValidationError

    def test_reserva_cancelada_no_cuenta_como_conflicto(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=5),
            estado=Reserva.Estado.CANCELADA,
        )
        libre = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=2),
            fecha_fin=self.hoy + timedelta(days=4),
        )
        libre.full_clean()  # no debe levantar ValidationError

    def test_editar_reserva_existente_no_choca_consigo_misma(self):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=5),
        )
        reserva.notas = 'actualizada'
        reserva.full_clean()  # no debe levantar ValidationError por chocar consigo misma


class ReservaCalculoTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.cliente = crear_cliente()
        self.vehiculo = crear_vehiculo(tarifa=Decimal('1500.00'))

    def test_dias_incluye_ambos_extremos(self):
        reserva = Reserva(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy,
            fecha_fin=self.hoy + timedelta(days=2),
        )
        self.assertEqual(reserva.dias, 3)

    def test_precio_total_se_calcula_al_guardar(self):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy,
            fecha_fin=self.hoy + timedelta(days=2),
        )
        self.assertEqual(reserva.precio_total, Decimal('4500.00'))


class ActualizarEstadoVehiculoTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.cliente = crear_cliente()
        self.vehiculo = crear_vehiculo()

    def test_vehiculo_pasa_a_rentado_con_reserva_activa_hoy(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy,
            fecha_fin=self.hoy + timedelta(days=2),
            estado=Reserva.Estado.CONFIRMADA,
        )
        actualizar_estado_vehiculo(self.vehiculo)
        self.vehiculo.refresh_from_db()
        self.assertEqual(self.vehiculo.estado, Vehiculo.Estado.RENTADO)

    def test_vehiculo_vuelve_a_disponible_sin_reserva_activa(self):
        self.vehiculo.estado = Vehiculo.Estado.RENTADO
        self.vehiculo.save(update_fields=['estado'])
        actualizar_estado_vehiculo(self.vehiculo)
        self.vehiculo.refresh_from_db()
        self.assertEqual(self.vehiculo.estado, Vehiculo.Estado.DISPONIBLE)


class LimpiarVideosEntregaVencidosTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.cliente = crear_cliente()
        self.vehiculo = crear_vehiculo()

    def _crear_reserva_devuelta(self, hace_dias):
        video = SimpleUploadedFile('entrega.mp4', b'contenido-falso', content_type='video/mp4')
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=hace_dias + 5),
            fecha_fin=self.hoy - timedelta(days=hace_dias),
            estado=Reserva.Estado.COMPLETADA,
            entrega_registrada=True,
            devolucion_registrada=True,
            video_entrega=video,
        )
        Reserva.objects.filter(pk=reserva.pk).update(
            devolucion_registrada_en=timezone.now() - timedelta(days=hace_dias),
        )
        return Reserva.objects.get(pk=reserva.pk)

    def test_borra_video_de_devolucion_antigua(self):
        reserva = self._crear_reserva_devuelta(hace_dias=31)
        self.assertTrue(reserva.video_entrega)

        borrados = limpiar_videos_entrega_vencidos(dias_gracia=30)

        self.assertEqual(borrados, 1)
        reserva.refresh_from_db()
        self.assertFalse(reserva.video_entrega)

    def test_no_borra_video_de_devolucion_reciente(self):
        reserva = self._crear_reserva_devuelta(hace_dias=5)

        borrados = limpiar_videos_entrega_vencidos(dias_gracia=30)

        self.assertEqual(borrados, 0)
        reserva.refresh_from_db()
        self.assertTrue(reserva.video_entrega)

    def test_no_toca_reservas_sin_devolucion_registrada(self):
        video = SimpleUploadedFile('entrega.mp4', b'contenido-falso', content_type='video/mp4')
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=40),
            fecha_fin=self.hoy - timedelta(days=35),
            estado=Reserva.Estado.ACTIVA,
            entrega_registrada=True,
            video_entrega=video,
        )

        borrados = limpiar_videos_entrega_vencidos(dias_gracia=30)

        self.assertEqual(borrados, 0)
        reserva.refresh_from_db()
        self.assertTrue(reserva.video_entrega)
