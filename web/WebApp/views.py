from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.cache import never_cache

from blog.models import Producto


def home(request):
    productos_destacados = (
        Producto.objects.select_related("region", "artesano")
        .prefetch_related("categorias")
        .filter(stock__gt=0)
        .order_by("-created")[:3]
    )
    return render(request, "WebApp/home.html", {"productos": productos_destacados})


def tienda(request):
    return render(request, "WebApp/tienda.html")


def offline(request):
    return render(request, "WebApp/offline.html", status=200)


def manifest(request):
    return JsonResponse(
        {
            "name": settings.PWA_APP_NAME,
            "short_name": settings.PWA_APP_SHORT_NAME,
            "start_url": reverse("Home"),
            "scope": "/",
            "display": "standalone",
            "background_color": settings.PWA_BACKGROUND_COLOR,
            "theme_color": settings.PWA_THEME_COLOR,
            "description": "Marketplace artesanal con experiencia instalable y soporte offline.",
            "lang": "es-MX",
            "icons": [
                {
                    "src": static("WebApp/img/pwa/icon-192.svg"),
                    "sizes": "192x192",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                },
                {
                    "src": static("WebApp/img/pwa/icon-512.svg"),
                    "sizes": "512x512",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                },
            ],
        }
    )


@never_cache
def service_worker(request):
    js = render_to_string(
        "WebApp/service-worker.js",
        {
            "static_version": "v1",
            "offline_url": reverse("offline"),
            "home_url": reverse("Home"),
            "catalogo_url": reverse("Blog"),
            "contacto_url": reverse("contacto"),
            "carro_url": reverse("carro:ver_carro"),
        },
    )
    return HttpResponse(js, content_type="application/javascript")
