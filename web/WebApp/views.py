from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from blog.models import Producto


def home(request):
    productos = Producto.objects.all()[:3]
    return render(request, "WebApp/home.html", {"productos": productos})


def tienda(request):
    return render(request, "WebApp/tienda.html")


def manifest(request):
    icon = staticfiles_storage.url("WebApp/img/principal.png")
    return JsonResponse(
        {
            "name": "Artesano Market",
            "short_name": "Artesano",
            "description": "Marketplace para artesanos locales y sus productos.",
            "start_url": reverse("Home"),
            "scope": "/",
            "display": "standalone",
            "background_color": "#f4ead6",
            "theme_color": "#6b705c",
            "lang": "es-MX",
            "icons": [
                {"src": icon, "sizes": "192x192", "type": "image/png"},
                {"src": icon, "sizes": "512x512", "type": "image/png"},
            ],
        },
        content_type="application/manifest+json",
    )


def service_worker(request):
    content = render_to_string(
        "WebApp/service-worker.js",
        {
            "home_url": reverse("Home"),
            "catalogo_url": reverse("Blog"),
            "carro_url": reverse("carro:ver_carro"),
            "css_url": staticfiles_storage.url("WebApp/css/gestion.css"),
            "bootstrap_css_url": staticfiles_storage.url("WebApp/vendor/bootstrap/css/bootstrap.min.css"),
            "bootstrap_js_url": staticfiles_storage.url("WebApp/vendor/bootstrap/js/bootstrap.bundle.min.js"),
            "jquery_url": staticfiles_storage.url("WebApp/vendor/jquery/jquery.min.js"),
            "cart_js_url": staticfiles_storage.url("WebApp/js/cart-sync.js"),
            "pwa_js_url": staticfiles_storage.url("WebApp/js/pwa-register.js"),
        },
    )
    return HttpResponse(content, content_type="application/javascript")
