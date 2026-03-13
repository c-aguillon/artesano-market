from django.shortcuts import render, redirect
from .carro import Carro
from blog.models import Producto

# Create your views here.

def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.agregar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))

def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.eliminar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))

def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.restar_producto(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'Home'))

def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    return redirect(request.META.get('HTTP_REFERER', 'Home'))

def ver_carro(request):
    return render(request, "carro/carro_detalle.html")
