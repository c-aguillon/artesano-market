from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .carro import Carro
from blog.models import Producto


def _guardar_en_perfil(request, carro_dict):
    """Persiste el carrito en el perfil del usuario."""
    if request.user.is_authenticated:
        request.user.perfil.set_carrito(carro_dict)


def _carro_response(request, carro):
    """Helper: construye el JSON estándar del estado del carro."""
    items = []
    for key, value in carro.carro.items():
        items.append({
            "producto_id": value["producto_id"],
            "nombre":      value["nombre"],
            "precio":      value["precio"],
            "cantidad":    value["cantidad"],
            "imagen":      value.get("imagen", ""),
        })

    total = sum(float(i["precio"]) for i in items)
    count = sum(i["cantidad"] for i in items)

    # Guardar en perfil en cada modificación
    _guardar_en_perfil(request, carro.carro)

    return JsonResponse({
        "ok":    True,
        "items": items,
        "total": f"{total:.2f}",
        "count": count,
    })


@login_required
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.agregar(producto=producto)
    return _carro_response(request, carro)


@login_required
def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.eliminar(producto=producto)
    return _carro_response(request, carro)


@login_required
def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.restar_producto(producto=producto)
    return _carro_response(request, carro)


@login_required
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    # Limpiar también en perfil
    _guardar_en_perfil(request, {})
    return JsonResponse({"ok": True, "items": [], "total": "0.00", "count": 0})


@login_required
def ver_carro(request):
    return render(request, "carro/carro_detalle.html")