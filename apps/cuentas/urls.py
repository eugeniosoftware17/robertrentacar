from django.urls import path

from .views import PanelLoginView, PanelLogoutView

app_name = 'cuentas'

urlpatterns = [
    path('login/', PanelLoginView.as_view(), name='login'),
    path('logout/', PanelLogoutView.as_view(), name='logout'),
]
