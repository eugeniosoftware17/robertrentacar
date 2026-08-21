import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.configuracion.models import ConfiguracionEmpresa
from apps.core.middleware import SESSION_ULTIMA_ACTIVIDAD
from apps.core.sync_permisos import sincronizar_permisos_grupos

User = get_user_model()


class InactividadSesionTests(TestCase):
    def setUp(self):
        sincronizar_permisos_grupos()
        self.admin = User.objects.create_superuser(
            username='admininact',
            email='admin@example.com',
            password='clave-segura-123',
        )
        config = ConfiguracionEmpresa.obtener()
        config.bloqueo_inactividad_horas = 1
        config.save(update_fields=['bloqueo_inactividad_horas'])

    def test_sesion_activa_no_cierra(self):
        self.client.force_login(self.admin)
        session = self.client.session
        session[SESSION_ULTIMA_ACTIVIDAD] = time.time() - 1800
        session.save()
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)

    def test_sesion_vencida_redirige_a_login(self):
        self.client.force_login(self.admin)
        session = self.client.session
        session[SESSION_ULTIMA_ACTIVIDAD] = time.time() - 7200
        session.save()
        respuesta = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            respuesta,
            f"{reverse('cuentas:login')}?inactividad=1",
            fetch_redirect_response=False,
        )

    def test_login_inicializa_marca_de_actividad(self):
        respuesta = self.client.post(reverse('cuentas:login'), {
            'username': 'admininact',
            'password': 'clave-segura-123',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(SESSION_ULTIMA_ACTIVIDAD, self.client.session)
