from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.finanzas.models import Gasto
from apps.mantenimiento.models import Mantenimiento
from apps.reservas.models import Reserva

from .models import Vehiculo
from .services import resumen_financiero


class ResumenFinancieroTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.vehiculo = Vehiculo.objects.create(
            marca='Toyota',
            modelo='Corolla',
            anio=2022,
            placa='RF00001',
            tarifa_diaria=Decimal('2000.00'),
            precio_compra=Decimal('900000.00'),
        )
        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='001-1111111-1',
            telefono='809-555-0000',
            licencia_numero='L-1',
            licencia_vence=self.hoy + timedelta(days=365),
        )

    def test_ingresos_suman_reservas_no_canceladas(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=10),
            fecha_fin=self.hoy - timedelta(days=8),
        )
        cancelada = Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=20),
            fecha_fin=self.hoy - timedelta(days=18),
        )
        cancelada.estado = Reserva.Estado.CANCELADA
        cancelada.save()

        resumen = resumen_financiero(self.vehiculo)
        self.assertEqual(resumen['ingresos'], Decimal('6000.00'))
        self.assertEqual(resumen['reservas_cantidad'], 1)

    def test_gastos_incluyen_mantenimiento_y_gastos_adicionales(self):
        Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            fecha=self.hoy,
            costo=Decimal('5000.00'),
        )
        Gasto.objects.create(
            concepto='Multa de tránsito',
            categoria=Gasto.Categoria.OTRO,
            monto=Decimal('1500.00'),
            fecha=self.hoy,
            vehiculo=self.vehiculo,
        )
        gasto_sin_vehiculo = Gasto.objects.create(
            concepto='Publicidad general',
            categoria=Gasto.Categoria.PUBLICIDAD,
            monto=Decimal('2000.00'),
            fecha=self.hoy,
        )

        resumen = resumen_financiero(self.vehiculo)
        self.assertEqual(resumen['gasto_mantenimiento'], Decimal('5000.00'))
        self.assertEqual(resumen['gasto_adicional'], Decimal('1500.00'))
        self.assertNotIn(gasto_sin_vehiculo, Gasto.objects.filter(vehiculo=self.vehiculo))

    def test_ganancia_neta_resta_precio_de_compra(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=10),
            fecha_fin=self.hoy - timedelta(days=8),
        )
        resumen = resumen_financiero(self.vehiculo)
        ganancia_esperada = resumen['ingresos'] - resumen['gastos_totales'] - self.vehiculo.precio_compra
        self.assertEqual(resumen['ganancia_neta'], ganancia_esperada)

    def test_filtra_por_rango_de_fechas(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=60),
            fecha_fin=self.hoy - timedelta(days=58),
        )
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy - timedelta(days=5),
            fecha_fin=self.hoy - timedelta(days=3),
        )

        resumen = resumen_financiero(self.vehiculo, desde=self.hoy - timedelta(days=10))
        self.assertEqual(resumen['reservas_cantidad'], 1)

    def test_sin_precio_compra_no_calcula_porcentaje_recuperado(self):
        self.vehiculo.precio_compra = Decimal('0.00')
        self.vehiculo.save(update_fields=['precio_compra'])
        resumen = resumen_financiero(self.vehiculo)
        self.assertIsNone(resumen['porcentaje_recuperado'])


class FotoUrlTests(TestCase):
    def setUp(self):
        self.vehiculo = Vehiculo.objects.create(
            marca='Kia',
            modelo='Rio',
            anio=2021,
            placa='FT00001',
            tarifa_diaria=Decimal('1500.00'),
        )

    def test_sin_foto_ni_link_no_hay_fotos(self):
        self.assertEqual(self.vehiculo.fotos_para_web(), [])
        self.assertFalse(self.vehiculo.tiene_foto)

    def test_usa_el_link_cuando_no_hay_archivo_subido(self):
        self.vehiculo.foto_url = 'https://example.com/kia-rio.jpg'
        self.vehiculo.save(update_fields=['foto_url'])

        fotos = self.vehiculo.fotos_para_web()
        self.assertEqual(len(fotos), 1)
        self.assertEqual(fotos[0].url, 'https://example.com/kia-rio.jpg')
        self.assertTrue(self.vehiculo.tiene_foto)

    def test_el_archivo_subido_tiene_prioridad_sobre_el_link(self):
        self.vehiculo.foto = SimpleUploadedFile('kia.jpg', b'contenido-falso', content_type='image/jpeg')
        self.vehiculo.foto_url = 'https://example.com/otra.jpg'
        self.vehiculo.save()

        fotos = self.vehiculo.fotos_para_web()
        self.assertEqual(len(fotos), 1)
        self.assertIn('kia', fotos[0].url)
