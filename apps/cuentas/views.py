from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
import time

from apps.core.middleware import SESSION_ULTIMA_ACTIVIDAD
from apps.core.permisos import url_inicio_panel

from .forms import LoginForm


class PanelLoginView(LoginView):
    template_name = 'cuentas/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return url_inicio_panel(self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session[SESSION_ULTIMA_ACTIVIDAD] = time.time()
        return response


class PanelLogoutView(LogoutView):
    next_page = reverse_lazy('cuentas:login')
