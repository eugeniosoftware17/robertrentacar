from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Empleado, Gasto, PagoNomina


class EmpleadoModelTests(TestCase):
    def test_nombre_completo(self):
        empleado = Empleado.objects.create(nombre='Ana', apellido='Ramírez', salario_base=Decimal('25000.00'))
        self.assertEqual(empleado.nombre_completo, 'Ana Ramírez')
        self.assertEqual(str(empleado), 'Ana Ramírez')


class FinanzasPanelTests(TestCase):
    """CRUD basico de nomina y gastos, protegido por permiso de modulo."""

    def setUp(self):
        self.hoy = timezone.localdate()
        self.admin = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='clave-segura-123',
        )
        self.empleado = Empleado.objects.create(
            nombre='Ana', apellido='Ramírez', puesto='Cajera', salario_base=Decimal('25000.00'),
        )

    def test_empleado_sin_permiso_no_accede_a_finanzas(self):
        empleado_user = get_user_model().objects.create_user(
            username='empleado1', password='clave-segura-123',
        )
        self.client.force_login(empleado_user)
        respuesta = self.client.get(reverse('finanzas:index'))
        self.assertEqual(respuesta.status_code, 403)

    def test_admin_puede_crear_pago_de_nomina(self):
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse('finanzas:nomina_crear'), {
            'empleado': self.empleado.pk,
            'concepto': PagoNomina.Concepto.SALARIO,
            'monto': '25000.00',
            'fecha_pago': self.hoy.isoformat(),
            'metodo': PagoNomina.Metodo.TRANSFERENCIA,
            'notas': '',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(PagoNomina.objects.count(), 1)
        pago = PagoNomina.objects.first()
        self.assertEqual(pago.empleado, self.empleado)
        self.assertEqual(pago.monto, Decimal('25000.00'))

    def test_admin_puede_crear_gasto_vinculado_a_vehiculo(self):
        from apps.vehiculos.models import CategoriaVehiculo, Vehiculo

        vehiculo = Vehiculo.objects.create(
            marca='Honda', modelo='CRV', anio=2021, placa='GX00001', tarifa_diaria=Decimal('3000.00'),
            categoria=CategoriaVehiculo.obtener_o_crear_default(),
        )
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse('finanzas:gasto_crear'), {
            'concepto': 'Cambio de aceite',
            'categoria': Gasto.Categoria.OTRO,
            'monto': '3500.00',
            'fecha': self.hoy.isoformat(),
            'vehiculo': vehiculo.pk,
            'notas': '',
        })
        self.assertEqual(respuesta.status_code, 302)
        gasto = Gasto.objects.get()
        self.assertEqual(gasto.vehiculo, vehiculo)
        self.assertEqual(gasto.monto, Decimal('3500.00'))

    def test_lista_de_gastos_filtra_por_rango_de_fechas(self):
        Gasto.objects.create(
            concepto='Dentro de rango', categoria=Gasto.Categoria.OTRO,
            monto=Decimal('100.00'), fecha=self.hoy,
        )
        Gasto.objects.create(
            concepto='Fuera de rango', categoria=Gasto.Categoria.OTRO,
            monto=Decimal('200.00'), fecha=self.hoy.replace(year=self.hoy.year - 1),
        )
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('finanzas:gastos_lista'), {
            'desde': self.hoy.isoformat(), 'hasta': self.hoy.isoformat(),
        })
        gastos = list(respuesta.context['gastos'])
        self.assertEqual(len(gastos), 1)
        self.assertEqual(gastos[0].concepto, 'Dentro de rango')
        self.assertEqual(respuesta.context['total'], Decimal('100.00'))

    def test_no_se_puede_eliminar_empleado_con_pagos_registrados(self):
        PagoNomina.objects.create(
            empleado=self.empleado, monto=Decimal('25000.00'), fecha_pago=self.hoy,
        )
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse('finanzas:empleado_eliminar', args=[self.empleado.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Empleado.objects.filter(pk=self.empleado.pk).exists())

    def test_nomina_rechaza_monto_cero(self):
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse('finanzas:nomina_crear'), {
            'empleado': self.empleado.pk,
            'concepto': PagoNomina.Concepto.SALARIO,
            'monto': '0',
            'fecha_pago': self.hoy.isoformat(),
            'metodo': PagoNomina.Metodo.EFECTIVO,
            'notas': '',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(PagoNomina.objects.count(), 0)

    def test_index_intercambia_fechas_invertidas(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('finanzas:index'), {
            'desde': self.hoy.isoformat(),
            'hasta': self.hoy.replace(day=1).isoformat(),
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['desde'], self.hoy.replace(day=1).isoformat())
        self.assertEqual(respuesta.context['hasta'], self.hoy.isoformat())
