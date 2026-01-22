# web/urls.py

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Distribuidores (o "Nuestros Aliados") - App: servicios
    path('aliados/', include('servicios.urls')), 

    # Catálogo de Productos (Tienda) - App: blog
    # Aquí vivirán: /catalogo/, /catalogo/producto/1, etc.
    path('catalogo/', include('blog.urls')),

    # Contacto - App: contacto
    path('contacto/', include('contacto.urls')),

    # Home / Inicio (La raíz del sitio) - App: WebApp
    path('', include('WebApp.urls')),
]

# Configuración para servir imágenes en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)