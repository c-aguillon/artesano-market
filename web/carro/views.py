from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import json

from blog.models import Producto

from .carro import Carro


def _guardar_en_perfil(request, carro_dict):
    if request.user.is_authenticated:
        request.user.perfil.set_carrito(carro_dict)


def _carro_response(request, carro, status=200, message=None):
    items = carro.get_items()
    payload = {
        "ok": status < 400,
        "items": items,
        "total": carro.get_total(),
        "count": carro.get_total_items(),
    }

    if message:
        payload["message"] = message

    _guardar_en_perfil(request, carro.carro)
    return JsonResponse(payload, status=status)


@login_required
def agregar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carro = Carro(request)

    cantidad_actual = 0
    item = carro.carro.get(str(producto.id))
    if item:
        cantidad_actual = int(item.get("cantidad", 0))

    if producto.stock <= 0:
        return _carro_response(request, carro, status=400, message="Este producto no tiene stock disponible.")

    if cantidad_actual >= producto.stock:
        return _carro_response(request, carro, status=400, message="Ya alcanzaste el stock disponible de este producto.")

    carro.agregar(producto=producto)
    return _carro_response(request, carro)


@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carro = Carro(request)
    carro.eliminar(producto=producto)
    return _carro_response(request, carro)


@login_required
def restar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carro = Carro(request)
    carro.restar_producto(producto=producto)
    return _carro_response(request, carro)


@login_required
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    _guardar_en_perfil(request, {})
    return JsonResponse({"ok": True, "items": [], "total": "0.00", "count": 0})


@login_required
def estado_carro(request):
    carro = Carro(request)
    return _carro_response(request, carro)


@login_required
@require_POST
def sincronizar_carro(request):
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "message": "Payload inválido."}, status=400)

    items = body.get("items", [])
    if not isinstance(items, list):
        return JsonResponse({"ok": False, "message": "Los items deben enviarse en una lista."}, status=400)

    producto_ids = [str(item.get("producto_id")) for item in items if item.get("producto_id")]
    productos = Producto.objects.filter(id__in=producto_ids)
    productos_por_id = {str(producto.id): producto for producto in productos}

    carro = Carro(request)
    carro.set_items(productos_por_id, items)
    return _carro_response(request, carro, message="Carrito sincronizado correctamente.")


@login_required
def ver_carro(request):
    return render(request, "carro/carro_detalle.html")
