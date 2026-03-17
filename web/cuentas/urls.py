from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registro/',  views.registro_view,        name='registro'),
    path('login/',     views.login_view,            name='login'),
    path('logout/',    views.logout_view,           name='logout'),
    path('dashboard/', views.dashboard_artesano,   name='dashboard_artesano'),
    # CRUD productos del artesano
    path('dashboard/producto/nuevo/',               views.producto_crear,    name='producto_crear'),
    path('dashboard/producto/<int:producto_id>/editar/',   views.producto_editar,   name='producto_editar'),
    path('dashboard/producto/<int:producto_id>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
]