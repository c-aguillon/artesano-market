from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .carro import Carro
from blog.models import Producto


@login_required
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.agregar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))


@login_required
def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.eliminar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))


@login_required
def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.restar_producto(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))


@login_required
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    return redirect(request.META.get('HTTP_REFERER', 'Home'))


@login_required
def ver_carro(request):
    return render(request, "carro/carro_detalle.html")