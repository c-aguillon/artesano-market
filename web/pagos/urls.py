from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("", views.pagos_view, name="pagar"),
    path("create-order", views.create_order, name="create_order"),
    path("capture-order", views.capture_order, name="capture_order"),
    path("exitoso/", views.orden_exitosa, name="orden_exitosa"),
]