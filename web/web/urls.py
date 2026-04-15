from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("aliados/", include("servicios.urls")),
    path("catalogo/", include("blog.urls")),
    path("contacto/", include("contacto.urls")),
    path("carro/", include("carro.urls")),
    path("pagar/", include("pagos.urls")),
    path("cuentas/", include("cuentas.urls")),
    path("", include("WebApp.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
