from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from blog.models import Categoria, Producto, Region


def blog(request):
    productos = Producto.objects.all().order_by("-created")
    categorias = Categoria.objects.all()
    regiones = Region.objects.all()

    region_id = request.GET.get("region")
    if region_id and region_id != "todas":
        productos = productos.filter(region__id=region_id)

    categorias_ids = request.GET.getlist("categoria")
    if categorias_ids:
        productos = productos.filter(categorias__id__in=categorias_ids).distinct()

    precio_max = request.GET.get("precio_max")
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for producto in productos:
            data.append(
                {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "descripcion": producto.descripcion,
                    "precio": str(producto.precio),
                    "imagen_url": producto.imagen.url if producto.imagen else None,
                    "categoria_nombre": producto.categorias.first().nombre if producto.categorias.exists() else None,
                    "detalle_url": reverse("producto_detalle", args=[producto.id]),
                    "agregar_carro_url": reverse("carro:agregar", args=[producto.id]),
                }
            )
        return JsonResponse({"productos": data})

    filtros_url = ""
    if region_id:
        filtros_url += f"&region={region_id}"
    if precio_max:
        filtros_url += f"&precio_max={precio_max}"
    for categoria_id in categorias_ids:
        filtros_url += f"&categoria={categoria_id}"

    paginator = Paginator(productos, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    contexto = {
        "posts": page_obj,
        "categorias": categorias,
        "regiones": regiones,
        "filtros_actuales": {
            "region": int(region_id) if region_id and region_id != "todas" else None,
            "categorias": [int(categoria_id) for categoria_id in categorias_ids],
            "precio_max": precio_max,
        },
        "filtros_url": filtros_url,
    }
    return render(request, "blog/blog.html", contexto)


def categoria(request, category_id):
    categoria_obj = get_object_or_404(Categoria, id=category_id)
    productos = Producto.objects.filter(categorias=categoria_obj)
    return render(request, "blog/categoria.html", {"categoria": categoria_obj, "posts": productos})


def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, "blog/producto_detalle.html", {"producto": producto})
