import json

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def get_paypal_token():
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise ValueError("PayPal no esta configurado.")

    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def pagos_view(request):
    return render(request, "pagos/pagos.html", {"paypal_client_id": settings.PAYPAL_CLIENT_ID})


@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    carro = request.session.get("carro", {})
    total = 0.0
    for item in carro.values():
        total += float(item.get("subtotal", item.get("precio", 0)))

    if total <= 0:
        return JsonResponse({"error": "El carrito esta vacio"}, status=400)

    try:
        token = get_paypal_token()
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "MXN", "value": f"{total:.2f}"}}],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        return JsonResponse({"error": "Error al crear orden", "detail": response.text}, status=500)

    return JsonResponse(response.json())


@csrf_exempt
def capture_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    body = json.loads(request.body)
    order_id = body.get("orderID")
    if not order_id:
        return JsonResponse({"error": "orderID requerido"}, status=400)

    try:
        token = get_paypal_token()
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    if not response.ok:
        return JsonResponse({"error": "Error al capturar pago", "detail": response.text}, status=500)

    data = response.json()

    from blog.models import Producto

    carro = request.session.get("carro", {})
    for item in carro.values():
        try:
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad_comprada = int(item.get("cantidad", 1))
            producto.stock = max(0, producto.stock - cantidad_comprada)
            producto.save()
        except Producto.DoesNotExist:
            pass

    items = list(carro.values())
    total = sum(float(item.get("subtotal", item.get("precio", 0))) for item in items)

    request.session["ultimo_pedido"] = {
        "order_id": order_id,
        "items": items,
        "total": f"{total:.2f}",
        "status": data.get("status", "COMPLETED"),
    }

    request.session["carro"] = {}
    request.session.modified = True
    if request.user.is_authenticated:
        request.user.perfil.set_carrito({})

    return JsonResponse({"status": "ok", "redirect": "/pagar/exitoso/"})


def orden_exitosa(request):
    pedido = request.session.get("ultimo_pedido", None)
    return render(request, "pagos/orden_exitosa.html", {"pedido": pedido})
