from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.core.models import AccesoModulo
from apps.core.permisos import (
    GRUPO_ADMIN,
    GRUPO_EMPLEADO,
    modulos_usuario,
    puede_acceder,
    url_inicio_panel,
)
from apps.core.sync_permisos import sincronizar_permisos_grupos
from apps.configuracion.forms import PermisosEmpleadoForm

User = get_user_model()


class PermisosPanelTests(TestCase):
    def setUp(self):
        sincronizar_permisos_grupos()
        self.admin = User.objects.create_superuser(
            username='adminperm',
            email='admin@example.com',
            password='clave-segura-123',
        )
        self.empleado = User.objects.create_user(
            username='empleadoperm',
            password='clave-segura-123',
        )
        Group.objects.get(name=GRUPO_EMPLEADO).user_set.add(self.empleado)

    def test_admin_ve_configuracion(self):
        self.assertIn('configuracion', modulos_usuario(self.admin))
        self.assertTrue(puede_acceder(self.admin, 'configuracion'))

    def test_empleado_no_ve_configuracion(self):
        AccesoModulo.objects.filter(modulo='configuracion').update(permitido=True)
        sincronizar_permisos_grupos()
        self.empleado = User.objects.get(pk=self.empleado.pk)
        self.assertNotIn('configuracion', modulos_usuario(self.empleado))
        self.assertFalse(puede_acceder(self.empleado, 'configuracion'))

    def test_empleado_sin_dashboard_redirige_a_modulo_permitido(self):
        AccesoModulo.objects.all().update(permitido=False)
        AccesoModulo.objects.filter(modulo='reservas').update(permitido=True)
        sincronizar_permisos_grupos()
        self.empleado = User.objects.get(pk=self.empleado.pk)
        self.assertEqual(url_inicio_panel(self.empleado), reverse('reservas:lista'))

    def test_guardar_permisos_actualiza_grupo_empleado(self):
        form = PermisosEmpleadoForm({
            'dashboard': True,
            'calendario': False,
            'vehiculos': False,
            'mantenimiento': False,
            'reservas': True,
            'clientes': False,
            'pagos': False,
            'reportes': False,
            'sitio_web': False,
            'finanzas': False,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.guardar()
        grupo = Group.objects.get(name=GRUPO_EMPLEADO)
        codenames = set(grupo.permissions.values_list('codename', flat=True))
        self.assertEqual(codenames, {'modulo_dashboard', 'modulo_reservas'})

    def test_empleado_sin_permiso_recibe_403_en_finanzas(self):
        self.client.force_login(self.empleado)
        respuesta = self.client.get(reverse('finanzas:index'))
        self.assertEqual(respuesta.status_code, 403)

    def test_crear_usuario_empleado_desde_formulario(self):
        from apps.configuracion.forms import CrearUsuarioPanelForm

        form = CrearUsuarioPanelForm({
            'username': 'nuevoemp',
            'first_name': 'Nuevo',
            'last_name': 'Empleado',
            'password1': 'clave-segura-123',
            'password2': 'clave-segura-123',
            'rol': GRUPO_EMPLEADO,
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.guardar()
        self.assertTrue(user.groups.filter(name=GRUPO_EMPLEADO).exists())
        self.assertTrue(modulos_usuario(user))

    def test_configuracion_solo_admin_en_panel(self):
        self.client.force_login(self.empleado)
        respuesta = self.client.get(reverse('configuracion:index'))
        self.assertEqual(respuesta.status_code, 403)

        admin_user = User.objects.create_user(
            username='adminpanel',
            password='clave-segura-123',
        )
        Group.objects.get(name=GRUPO_ADMIN).user_set.add(admin_user)
        self.client.force_login(admin_user)
        respuesta = self.client.get(reverse('configuracion:index'))
        self.assertEqual(respuesta.status_code, 200)
