from django.core.paginator import Paginator # <--- IMPORTAR ESTO AL INICIO
from django.shortcuts import render, get_object_or_404
from blog.models import Producto, Categoria, Region # <--- AQUÍ ESTABA EL ERROR (Ya usamos los nombres nuevos)

# Vista para el Catálogo General
def blog(request):
    # 1. Base y Filtros (Igual que antes)
    productos = Producto.objects.all().order_by('-created') # Es bueno ordenar siempre
    categorias = Categoria.objects.all()
    regiones = Region.objects.all()

    # --- LÓGICA DE FILTRADO ---
    region_id = request.GET.get('region')
    if region_id and region_id != 'todas':
        productos = productos.filter(region__id=region_id)

    categorias_ids = request.GET.getlist('categoria') 
    if categorias_ids:
        productos = productos.filter(categorias__id__in=categorias_ids).distinct()

    precio_max = request.GET.get('precio_max')
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # --- NUEVO: CONSTRUIR STRING DE FILTROS PARA LA URL ---
    # Esto es vital: guarda los filtros actuales en un texto para pegarlo a los links de página
    filtros_url = ""
    if region_id: filtros_url += f"&region={region_id}"
    if precio_max: filtros_url += f"&precio_max={precio_max}"
    for cat in categorias_ids: filtros_url += f"&categoria={cat}"

    # --- NUEVO: PAGINACIÓN ---
    # "6" es el número de productos por página. Cámbialo si quieres más.
    paginator = Paginator(productos, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'posts': page_obj, # Ahora 'posts' ya no son todos, son solo los de esta página
        'categorias': categorias,
        'regiones': regiones,
        'filtros_actuales': {
            'region': int(region_id) if region_id and region_id != 'todas' else None,
            'categorias': [int(c) for c in categorias_ids],
            'precio_max': precio_max
        },
        'filtros_url': filtros_url # Enviamos el string mágico al HTML
    }
    
    return render(request, "blog/blog.html", contexto)
    # 1. Base: Traemos todos los productos
    productos = Producto.objects.all()
    
    # 2. Traemos las opciones para llenar los filtros
    categorias = Categoria.objects.all()
    regiones = Region.objects.all()

    # --- LÓGICA DE FILTRADO ---
    
    # A) Filtrar por REGIÓN
    region_id = request.GET.get('region')
    if region_id and region_id != 'todas':
        productos = productos.filter(region__id=region_id)

    # B) Filtrar por CATEGORÍA (Checkbox múltiples)
    # getlist obtiene una lista de todos los checkboxes marcados
    categorias_ids = request.GET.getlist('categoria') 
    if categorias_ids:
        productos = productos.filter(categorias__id__in=categorias_ids).distinct()

    # C) Filtrar por PRECIO MÁXIMO
    precio_max = request.GET.get('precio_max')
    if precio_max:
        # __lte significa "Less Than or Equal" (Menor o igual que)
        productos = productos.filter(precio__lte=precio_max)

    # 3. Contexto: Enviamos todo al HTML
    # Enviamos también los valores seleccionados para que el formulario no se "reinicie"
    contexto = {
        'posts': productos,
        'categorias': categorias,
        'regiones': regiones,
        'filtros_actuales': {
            'region': int(region_id) if region_id and region_id != 'todas' else None,
            'categorias': [int(c) for c in categorias_ids], # Lista de IDs enteros
            'precio_max': precio_max
        }
    }
    
    return render(request, "blog/blog.html", contexto)

# Vista para Filtrar por Categoría
def categoria(request, category_id):
    # Busamos la categoría o devolvemos error 404 si no existe
    categoria = get_object_or_404(Categoria, id=category_id)
    
    # Filtramos los productos de esa categoría
    productos = Producto.objects.filter(categorias=categoria)
    
    # Mantenemos la clave "posts" temporalmente
    return render(request, "blog/categoria.html", {'categoria': categoria, 'posts': productos})

def producto_detalle(request, producto_id):
    # Buscamos el producto por su ID. Si no existe, lanza error 404 automáticamente.
    producto = get_object_or_404(Producto, id=producto_id)
    
    return render(request, "blog/producto_detalle.html", {'producto': producto})