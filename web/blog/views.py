from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from blog.models import Producto, Categoria, Region


def blog(request):

    productos = Producto.objects.all().order_by('-created')
    categorias = Categoria.objects.all()
    regiones = Region.objects.all()

    # ---------------- FILTROS ----------------
    region_id = request.GET.get('region')
    if region_id and region_id != 'todas':
        productos = productos.filter(region__id=region_id)

    categorias_ids = request.GET.getlist('categoria')
    if categorias_ids:
        productos = productos.filter(categorias__id__in=categorias_ids).distinct()

    precio_max = request.GET.get('precio_max')
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # ---------------- PAGINACIÓN ----------------
    paginator = Paginator(productos, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'posts': page_obj,
        'categorias': categorias,
        'regiones': regiones,
        'filtros_actuales': {
            'region': int(region_id) if region_id and region_id != 'todas' else None,
            'categorias': [int(c) for c in categorias_ids],
            'precio_max': precio_max
        }
    }

    # PETICIÓN AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'blog/partials/productos.html',
            contexto,
            request=request
        )
        return JsonResponse({'html': html})

    return render(request, "blog/blog.html", contexto)


def categoria(request, category_id):
    categoria = get_object_or_404(Categoria, id=category_id)
    productos = Producto.objects.filter(categorias=categoria)
    return render(request, "blog/categoria.html", {'categoria': categoria, 'posts': productos})


def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, "blog/producto_detalle.html", {'producto': producto})
