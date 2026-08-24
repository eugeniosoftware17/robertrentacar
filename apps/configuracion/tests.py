from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.core.permisos import GRUPO_DUENO, GRUPO_EMPLEADO
from apps.core.sync_permisos import sincronizar_permisos_grupos

User = get_user_model()


class ContratoDemoConfiguracionTests(TestCase):
    def setUp(self):
        sincronizar_permisos_grupos()
        self.admin = User.objects.create_superuser(
            username='admindemo',
            email='admin@example.com',
            password='clave-segura-123',
        )
        self.dueno = User.objects.create_user(username='duenodemo', password='clave-segura-123')
        Group.objects.get(name=GRUPO_DUENO).user_set.add(self.dueno)
        self.empleado = User.objects.create_user(username='empdemo', password='clave-segura-123')
        Group.objects.get(name=GRUPO_EMPLEADO).user_set.add(self.empleado)

    def test_admin_ve_contrato_demo(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('configuracion:contrato_demo'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ejemplo — datos ficticios')
        self.assertContains(respuesta, 'Juan Pérez')

    def test_dueno_no_accede_a_contrato_demo(self):
        self.client.force_login(self.dueno)
        respuesta = self.client.get(reverse('configuracion:contrato_demo'))
        self.assertEqual(respuesta.status_code, 403)
