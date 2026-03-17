from django.shortcuts import render

# Create your views here.

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json


def get_paypal_token():
    """Obtiene el access token de PayPal usando client credentials."""
    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def pagos_view(request):
    """Renderiza la pantalla de pago."""
    return render(request, "pagos/pagos.html", {
        "paypal_client_id": settings.PAYPAL_CLIENT_ID,
    })


@csrf_exempt
def create_order(request):
    """Crea una orden en PayPal con el total del carrito."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # Obtener total del carrito desde la sesión
    carro = request.session.get("carro", {})
    total = 0.0
    for item in carro.values():
        total += float(item.get("precio", 0)) * int(item.get("cantidad", 1))

    if total <= 0:
        return JsonResponse({"error": "El carrito está vacío"}, status=400)

    token = get_paypal_token()
    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MXN",
                    "value": f"{total:.2f}",
                }
            }
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        return JsonResponse({"error": "Error al crear orden", "detail": response.text}, status=500)

    return JsonResponse(response.json())


@csrf_exempt
def capture_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    body = json.loads(request.body)
    order_id = body.get("orderID")

    if not order_id:
        return JsonResponse({"error": "orderID requerido"}, status=400)

    token = get_paypal_token()
    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(url, headers=headers)
    if not response.ok:
        return JsonResponse({"error": "Error al capturar pago", "detail": response.text}, status=500)

    data = response.json()

    # ✅ Descontar stock de cada producto comprado
    from blog.models import Producto
    carro = request.session.get("carro", {})

    for item in carro.values():
        try:
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad_comprada = int(item.get("cantidad", 1))
            # No bajar de 0
            producto.stock = max(0, producto.stock - cantidad_comprada)
            producto.save()
        except Producto.DoesNotExist:
            pass  # Si el producto fue eliminado, ignorar

    # Guardar resumen en sesión
    items = list(carro.values())
    total = sum(float(i.get("precio", 0)) * int(i.get("cantidad", 1)) for i in items)

    request.session["ultimo_pedido"] = {
        "order_id": order_id,
        "items": items,
        "total": f"{total:.2f}",
        "status": data.get("status", "COMPLETED"),
    }

    # Limpiar carrito
    request.session["carro"] = {}
    request.session.modified = True

    return JsonResponse({"status": "ok", "redirect": "/pagar/exitoso/"})


def orden_exitosa(request):
    pedido = request.session.get("ultimo_pedido", None)
    return render(request, "pagos/orden_exitosa.html", {"pedido": pedido})