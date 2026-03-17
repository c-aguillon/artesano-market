from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal del catálogo: Llama a la función 'blog' en views.py
    path('', views.blog, name="Blog"),

    # Ruta de filtrado: Llama a la función 'categoria' en views.py
    # Nota: Usamos <int:category_id> para coincidir con el argumento en la vista
    path('categoria/<int:category_id>/', views.categoria, name="categoria"),
    path('producto/<int:producto_id>/', views.producto_detalle, name="producto_detalle"),
]
