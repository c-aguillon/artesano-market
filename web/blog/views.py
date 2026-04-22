from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Categoria, Producto, Region


PRODUCTOS_POR_PAGINA = 6


def _productos_base():
    return (
        Producto.objects.select_related("region", "artesano")
        .prefetch_related("categorias")
        .order_by("-created")
    )


def _aplicar_filtros(request, productos):
    region_id = request.GET.get("region")
    categorias_ids = request.GET.getlist("categoria")
    precio_max = request.GET.get("precio_max")

    if region_id and region_id != "todas":
        productos = productos.filter(region__id=region_id)

    if categorias_ids:
        productos = productos.filter(categorias__id__in=categorias_ids).distinct()

    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    return productos, region_id, categorias_ids, precio_max


def _filtros_url(region_id, categorias_ids, precio_max):
    filtros = []

    if region_id:
        filtros.append(f"region={region_id}")

    if precio_max:
        filtros.append(f"precio_max={precio_max}")

    for categoria_id in categorias_ids:
        filtros.append(f"categoria={categoria_id}")

    return "".join(f"&{filtro}" for filtro in filtros)


def blog(request):
    productos, region_id, categorias_ids, precio_max = _aplicar_filtros(
        request,
        _productos_base(),
    )
    categorias = Categoria.objects.order_by("nombre")
    regiones = Region.objects.order_by("nombre")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = [
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
            for producto in productos
        ]
        return JsonResponse({"productos": data})

    paginator = Paginator(productos, PRODUCTOS_POR_PAGINA)
    page_obj = paginator.get_page(request.GET.get("page"))

    contexto = {
        "posts": page_obj,
        "categorias": categorias,
        "regiones": regiones,
        "filtros_actuales": {
            "region": int(region_id) if region_id and region_id != "todas" else None,
            "categorias": [int(categoria_id) for categoria_id in categorias_ids],
            "precio_max": precio_max,
        },
        "filtros_url": _filtros_url(region_id, categorias_ids, precio_max),
    }
    return render(request, "blog/blog.html", contexto)


def categoria(request, category_id):
    categoria_actual = get_object_or_404(Categoria, id=category_id)
    productos = _productos_base().filter(categorias=categoria_actual)
    return render(
        request,
        "blog/categoria.html",
        {"categoria": categoria_actual, "posts": productos},
    )


def producto_detalle(request, producto_id):
    producto = get_object_or_404(
        _productos_base(),
        id=producto_id,
    )
    return render(request, "blog/producto_detalle.html", {"producto": producto})
