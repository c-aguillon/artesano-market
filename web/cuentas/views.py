from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioRegistro, FormularioLogin
from .forms import FormularioProducto
from blog.models import Producto
from django.shortcuts import get_object_or_404


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}!')
            # Redirige según rol
            if user.perfil.es_artesano():
                return redirect('cuentas:dashboard_artesano')
            return redirect('Home')
    else:
        form = FormularioRegistro()
    return render(request, 'cuentas/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        form = FormularioLogin(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                if user.perfil.es_artesano():
                    return redirect('cuentas:dashboard_artesano')
                return redirect('Home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = FormularioLogin()
    return render(request, 'cuentas/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('Home')


@login_required
def dashboard_artesano(request):
    # Solo artesanos pueden entrar
    if not request.user.perfil.es_artesano():
        messages.error(request, 'No tienes permiso para acceder aquí.')
        return redirect('Home')
    # Productos del artesano logueado
    from blog.models import Producto
    productos = Producto.objects.filter(artesano=request.user)
    return render(request, 'cuentas/dashboard_artesano.html', {'productos': productos})

@login_required
def producto_crear(request):
    if not request.user.perfil.es_artesano():
        messages.error(request, 'No tienes permiso para esto.')
        return redirect('Home')

    if request.method == 'POST':
        form = FormularioProducto(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.artesano = request.user
            producto.save()
            form.save_m2m()  # Guarda las categorías (ManyToMany)
            messages.success(request, f'"{producto.nombre}" publicado correctamente.')
            return redirect('cuentas:dashboard_artesano')
    else:
        form = FormularioProducto()

    return render(request, 'cuentas/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'boton': 'Publicar producto'
    })


@login_required
def producto_editar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, artesano=request.user)

    if request.method == 'POST':
        form = FormularioProducto(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{producto.nombre}" actualizado correctamente.')
            return redirect('cuentas:dashboard_artesano')
    else:
        form = FormularioProducto(instance=producto)

    return render(request, 'cuentas/producto_form.html', {
        'form': form,
        'titulo': 'Editar Producto',
        'boton': 'Guardar cambios',
        'producto': producto
    })


@login_required
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, artesano=request.user)

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'"{nombre}" eliminado correctamente.')
        return redirect('cuentas:dashboard_artesano')

    return render(request, 'cuentas/producto_confirmar_eliminar.html', {
        'producto': producto
    })