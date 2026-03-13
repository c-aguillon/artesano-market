from django.shortcuts import render, HttpResponse
from blog.models import Producto

# Create your views here.
def home(request):
    productos = Producto.objects.all()[:3]
    return render(request,"WebApp/home.html", {"productos": productos})

def tienda(request):
    return render(request,"WebApp/tienda.html")

