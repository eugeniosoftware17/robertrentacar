from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginForm


class PanelLoginView(LoginView):
    template_name = 'cuentas/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class PanelLogoutView(LogoutView):
    next_page = reverse_lazy('cuentas:login')
