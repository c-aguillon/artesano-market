import json

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from blog.models import Producto
from carro.carro import Carro


def get_paypal_token():
    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def pagos_view(request):
    carro = Carro(request)
    return render(
        request,
        "pagos/pagos.html",
        {
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
            "total_carro": carro.get_total(),
        },
    )


@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    carro = Carro(request)
    total = carro.get_total()

    if float(total) <= 0:
        return JsonResponse({"error": "El carrito está vacío"}, status=400)

    token = get_paypal_token()
    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MXN",
                    "value": total,
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
        return JsonResponse(
            {"error": "Error al crear orden", "detail": response.text},
            status=500,
        )

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
        return JsonResponse(
            {"error": "Error al capturar pago", "detail": response.text},
            status=500,
        )

    data = response.json()
    carro = Carro(request)
    items = carro.get_items()

    for item in items:
        try:
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad_comprada = int(item.get("cantidad", 1))
            producto.stock = max(0, producto.stock - cantidad_comprada)
            producto.save(update_fields=["stock"])
        except Producto.DoesNotExist:
            continue

    request.session["ultimo_pedido"] = {
        "order_id": order_id,
        "items": items,
        "total": carro.get_total(),
        "status": data.get("status", "COMPLETED"),
    }

    carro.limpiar_carro()
    request.session.modified = True

    return JsonResponse({"status": "ok", "redirect": "/pagar/exitoso/"})


def orden_exitosa(request):
    pedido = request.session.get("ultimo_pedido")
    return render(request, "pagos/orden_exitosa.html", {"pedido": pedido})
