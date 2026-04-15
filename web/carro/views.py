import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods

from blog.models import Producto

from .carro import Carro


def _guardar_en_perfil(request, carro_dict):
    if request.user.is_authenticated:
        request.user.perfil.set_carrito(carro_dict)


def _cart_items(carro):
    items = []
    for value in carro.carro.values():
        items.append(
            {
                "producto_id": value["producto_id"],
                "nombre": value["nombre"],
                "precio": value["precio"],
                "precio_unitario": value.get("precio_unitario", value["precio"]),
                "subtotal": value.get("subtotal", value["precio"]),
                "cantidad": value["cantidad"],
                "imagen": value.get("imagen", ""),
            }
        )
    return items


def _carro_response(request, carro):
    items = _cart_items(carro)
    total = sum(Decimal(item["subtotal"]) for item in items) if items else Decimal("0.00")
    count = sum(item["cantidad"] for item in items)

    _guardar_en_perfil(request, carro.carro)

    return JsonResponse(
        {
            "ok": True,
            "items": items,
            "total": f"{total:.2f}",
            "count": count,
        }
    )


def _construir_carro_desde_items(items):
    ids = []
    for item in items:
        try:
            ids.append(int(item.get("producto_id")))
        except (TypeError, ValueError):
            continue

    productos = {producto.id: producto for producto in Producto.objects.filter(id__in=ids)}
    carro_dict = {}

    for item in items:
        try:
            producto_id = int(item.get("producto_id"))
            cantidad = max(int(item.get("cantidad", 1)), 1)
        except (TypeError, ValueError):
            continue

        producto = productos.get(producto_id)
        if not producto:
            continue

        if producto.stock > 0:
            cantidad = min(cantidad, producto.stock)

        carro_dict[str(producto_id)] = Carro.crear_item(producto, cantidad=cantidad)

    return carro_dict


@login_required
@require_GET
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carro.agregar(producto=producto)
    return _carro_response(request, carro)


@login_required
@require_GET
def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carro.eliminar(producto=producto)
    return _carro_response(request, carro)


@login_required
@require_GET
def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carro.restar_producto(producto=producto)
    return _carro_response(request, carro)


@login_required
@require_GET
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    _guardar_en_perfil(request, {})
    return JsonResponse({"ok": True, "items": [], "total": "0.00", "count": 0})


@login_required
@require_GET
def estado_carro(request):
    return _carro_response(request, Carro(request))


@login_required
@require_http_methods(["POST"])
def sincronizar_carro(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON invalido"}, status=400)

    items = payload.get("items", [])
    carro = Carro(request)
    carro.reemplazar(_construir_carro_desde_items(items))
    return _carro_response(request, carro)


@login_required
def ver_carro(request):
    return render(request, "carro/carro_detalle.html")
