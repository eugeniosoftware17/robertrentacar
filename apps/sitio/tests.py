from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.reservas.models import Reserva
from apps.vehiculos.models import Vehiculo

from .forms import ConfiguracionSitioForm, PaginaInformativaForm, ReservaWebForm
from .models import ConfiguracionSitio, PaginaInformativa
from .services import tiene_conflicto_reserva, vehiculo_reservable


def crear_vehiculo(placa='A123456', **extra):
    defaults = {
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'anio': 2022,
        'placa': placa,
        'tarifa_diaria': Decimal('2000.00'),
        'activo': True,
        'visible_en_web': True,
    }
    defaults.update(extra)
    return Vehiculo.objects.create(**defaults)


def datos_formulario(vehiculo, hoy, **extra):
    data = {
        'vehiculo': vehiculo.pk,
        'fecha_inicio': (hoy + timedelta(days=2)).isoformat(),
        'fecha_fin': (hoy + timedelta(days=4)).isoformat(),
        'nombre': 'Ana',
        'apellido': 'Gómez',
        'documento': '001-0000001-1',
        'telefono': '809-555-1111',
        'email': 'ana@example.com',
        'licencia_numero': 'L-1',
        'licencia_vence': (hoy + timedelta(days=365)).isoformat(),
        'notas': '',
    }
    data.update(extra)
    return data


class ReservaWebFormClienteTests(TestCase):
    """Cubre el bug corregido: la reserva web no debe pisar un cliente existente."""

    def setUp(self):
        self.hoy = timezone.localdate()
        self.vehiculo = crear_vehiculo()
        ConfiguracionSitio.obtener()

    def test_honeypot_lleno_invalida_el_formulario(self):
        datos = datos_formulario(self.vehiculo, self.hoy, empresa_web='http://spam.example')
        form = ReservaWebForm(datos, vehiculo=self.vehiculo)
        self.assertFalse(form.is_valid())
        self.assertIn('empresa_web', form.errors)

    def test_documento_nuevo_crea_cliente(self):
        form = ReservaWebForm(datos_formulario(self.vehiculo, self.hoy), vehiculo=self.vehiculo)
        self.assertTrue(form.is_valid(), form.errors)
        reserva = form.guardar_reserva()
        self.assertEqual(reserva.cliente.documento, '001-0000001-1')
        self.assertEqual(reserva.cliente.telefono, '809-555-1111')

    def test_documento_existente_no_sobrescribe_datos_del_cliente(self):
        cliente_original = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='001-0000001-1',
            telefono='809-000-0000',
            email='juan.real@example.com',
            licencia_numero='L-ORIGINAL',
            licencia_vence=self.hoy + timedelta(days=365),
        )

        datos = datos_formulario(
            self.vehiculo,
            self.hoy,
            documento='001-0000001-1',
            nombre='Otra Persona',
            telefono='809-999-9999',
            email='otro@example.com',
        )
        form = ReservaWebForm(datos, vehiculo=self.vehiculo)
        self.assertTrue(form.is_valid(), form.errors)
        reserva = form.guardar_reserva()

        cliente_original.refresh_from_db()
        self.assertEqual(reserva.cliente_id, cliente_original.pk)
        self.assertEqual(cliente_original.nombre, 'Juan')
        self.assertEqual(cliente_original.telefono, '809-000-0000')
        self.assertEqual(cliente_original.email, 'juan.real@example.com')
        self.assertIn('809-999-9999', reserva.notas)


class CampoAvanzadoSoloAdminTests(TestCase):
    """El código HTML/CSS/JS libre solo debe poder tocarlo un administrador."""

    def test_empleado_no_puede_modificar_css_js_global(self):
        config = ConfiguracionSitio.obtener()
        config.css_global = 'body { color: red; }'
        config.save(update_fields=['css_global'])

        form = ConfiguracionSitioForm(
            {
                'home_titulo': 'Título nuevo',
                'home_diseno': ConfiguracionSitio.HomeDiseno.CLASICO,
                'home_fondo_opacidad': 60,
                'home_fondo_posicion': ConfiguracionSitio.FondoPosicion.CENTRO,
                'home_fondo_tamano': ConfiguracionSitio.FondoTamano.CUBRIR,
                'anticipacion_horas': 24,
                'css_global': 'body { color: red; } /* inyectado */',
                'js_global': 'alert(document.cookie)',
                'home_html_extra': '<script>robar()</script>',
            },
            instance=config,
            restringir_avanzado=True,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('css_global', form.fields)
        self.assertNotIn('js_global', form.fields)
        self.assertNotIn('home_html_extra', form.fields)

        guardado = form.save()
        self.assertEqual(guardado.css_global, 'body { color: red; }')
        self.assertEqual(guardado.js_global, '')
        self.assertEqual(guardado.home_html_extra, '')

    def test_admin_si_puede_modificar_css_js_global(self):
        config = ConfiguracionSitio.obtener()
        form = ConfiguracionSitioForm(
            {
                'home_titulo': 'Título nuevo',
                'home_diseno': ConfiguracionSitio.HomeDiseno.CLASICO,
                'home_fondo_opacidad': 60,
                'home_fondo_posicion': ConfiguracionSitio.FondoPosicion.CENTRO,
                'home_fondo_tamano': ConfiguracionSitio.FondoTamano.CUBRIR,
                'anticipacion_horas': 24,
                'css_global': 'body { color: blue; }',
            },
            instance=config,
            restringir_avanzado=False,
        )
        self.assertTrue(form.is_valid(), form.errors)
        guardado = form.save()
        self.assertEqual(guardado.css_global, 'body { color: blue; }')

    def test_empleado_no_puede_modificar_css_js_de_pagina(self):
        pagina = PaginaInformativa.objects.create(
            slug='nosotros',
            titulo='Nosotros',
            contenido='<p>Hola</p>',
            css_extra='.original { color: green; }',
        )
        form = PaginaInformativaForm(
            {
                'slug': 'nosotros',
                'titulo': 'Nosotros',
                'contenido': '<p>Hola</p>',
                'css_extra': '.inyectado { color: red; }',
                'js_extra': 'alert(1)',
                'orden': 0,
                'publicada': True,
                'en_menu': True,
            },
            instance=pagina,
            restringir_avanzado=True,
        )
        self.assertTrue(form.is_valid(), form.errors)
        guardado = form.save()
        self.assertEqual(guardado.css_extra, '.original { color: green; }')
        self.assertEqual(guardado.js_extra, '')


class DisponibilidadWebTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.vehiculo = crear_vehiculo()
        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='001-0000009-9',
            telefono='809-555-0000',
            licencia_numero='L-1',
            licencia_vence=self.hoy + timedelta(days=365),
        )

    def test_vehiculo_no_visible_en_web_no_es_reservable(self):
        self.vehiculo.visible_en_web = False
        self.vehiculo.save(update_fields=['visible_en_web'])
        self.assertFalse(vehiculo_reservable(self.vehiculo))

    def test_vehiculo_en_mantenimiento_no_es_reservable_si_config_lo_bloquea(self):
        config = ConfiguracionSitio.obtener()
        config.bloquear_mantenimiento = True
        config.save(update_fields=['bloquear_mantenimiento'])
        self.vehiculo.estado = Vehiculo.Estado.MANTENIMIENTO
        self.vehiculo.save(update_fields=['estado'])
        self.assertFalse(vehiculo_reservable(self.vehiculo))

    def test_tiene_conflicto_reserva_detecta_solape(self):
        Reserva.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            fecha_inicio=self.hoy + timedelta(days=1),
            fecha_fin=self.hoy + timedelta(days=5),
        )
        self.assertTrue(
            tiene_conflicto_reserva(self.vehiculo, self.hoy + timedelta(days=3), self.hoy + timedelta(days=8))
        )
        self.assertFalse(
            tiene_conflicto_reserva(self.vehiculo, self.hoy + timedelta(days=6), self.hoy + timedelta(days=8))
        )


class ReservaWebRateLimitTests(TestCase):
    """El envío repetido del formulario público debe frenarse por IP."""

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.hoy = timezone.localdate()
        self.vehiculo = crear_vehiculo(placa='B999999')
        ConfiguracionSitio.obtener()
        self.url = reverse('sitio:reservar', kwargs={'slug': self.vehiculo.slug})

    def test_bloquea_despues_de_varios_intentos_seguidos(self):
        datos = datos_formulario(self.vehiculo, self.hoy, documento='001-0000005-5')
        for _ in range(5):
            respuesta = self.client.post(self.url, datos)
            self.assertNotEqual(respuesta.status_code, 429)

        respuesta = self.client.post(self.url, datos)
        self.assertEqual(respuesta.status_code, 429)
