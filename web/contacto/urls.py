from django.urls import path
from . import views

urlpatterns = [
    path('', views.contacto, name='contacto'),
    path('enviar/', views.contacto_enviar, name='contacto_enviar'),
]