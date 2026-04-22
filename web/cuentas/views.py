from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme

from blog.models import Producto

from .forms import FormularioLogin, FormularioProducto, FormularioRegistro


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _get_safe_redirect(request, default="Home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default


def _form_errors(form):
    return {field: [error["message"] for error in errors] for field, errors in form.errors.get_json_data().items()}


def _producto_payload(producto, request):
    categoria = producto.categorias.first()
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": f"{producto.precio:.2f}",
        "stock": producto.stock,
        "region": str(producto.region) if producto.region else "Sin región",
        "categoria": categoria.nombre if categoria else "—",
        "imagen_url": producto.imagen.url if producto.imagen else "",
        "editar_url": request.build_absolute_uri(f"/cuentas/dashboard/producto/{producto.id}/editar/"),
        "eliminar_url": request.build_absolute_uri(f"/cuentas/dashboard/producto/{producto.id}/eliminar/"),
    }


def _dashboard_stats(productos):
    total_productos = productos.count()
    inventario_total = sum(producto.stock for producto in productos)
    return {
        "productos_publicados": total_productos,
        "inventario_total": inventario_total,
    }


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("Home")

    next_url = _get_safe_redirect(request)
    if request.method == "POST":
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            redirect_url = next_url if next_url != "Home" else (
                "/cuentas/dashboard/" if user.perfil.es_artesano() else "/"
            )

            if _is_ajax(request):
                return JsonResponse(
                    {
                        "ok": True,
                        "message": f"¡Bienvenido, {user.first_name or user.username}!",
                        "redirect": redirect_url,
                    }
                )

            messages.success(request, f"¡Bienvenido, {user.first_name or user.username}!")
            return redirect(redirect_url)

        if _is_ajax(request):
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Revisa los campos del formulario.",
                    "errors": _form_errors(form),
                },
                status=400,
            )
    else:
        form = FormularioRegistro()

    return render(
        request,
        "cuentas/registro.html",
        {"form": form, "next_url": next_url if next_url != "Home" else ""},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("Home")

    next_url = _get_safe_redirect(request)
    if request.method == "POST":
        form = FormularioLogin(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)

                carrito_guardado = user.perfil.get_carrito()
                if carrito_guardado and not request.session.get("carro"):
                    request.session["carro"] = carrito_guardado
                    request.session.modified = True

                redirect_url = next_url if next_url != "Home" else (
                    "/cuentas/dashboard/" if user.perfil.es_artesano() else "/"
                )

                if _is_ajax(request):
                    return JsonResponse({"ok": True, "redirect": redirect_url})

                return redirect(redirect_url)

            error_message = "Usuario o contraseña incorrectos."
            if _is_ajax(request):
                return JsonResponse({"ok": False, "message": error_message}, status=400)
            messages.error(request, error_message)
        elif _is_ajax(request):
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Revisa los datos ingresados.",
                    "errors": _form_errors(form),
                },
                status=400,
            )
    else:
        form = FormularioLogin()

    return render(
        request,
        "cuentas/login.html",
        {"form": form, "next_url": next_url if next_url != "Home" else ""},
    )


def logout_view(request):
    logout(request)
    if _is_ajax(request):
        return JsonResponse({"ok": True, "redirect": "/"})
    return redirect("Home")


@login_required
def dashboard_artesano(request):
    if not request.user.perfil.es_artesano():
        messages.error(request, "No tienes permiso para acceder aquí.")
        return redirect("Home")

    productos = (
        Producto.objects.filter(artesano=request.user)
        .select_related("region")
        .prefetch_related("categorias")
        .order_by("-created")
    )
    return render(
        request,
        "cuentas/dashboard_artesano.html",
        {
            "productos": productos,
            "stats": _dashboard_stats(productos),
        },
    )


@login_required
def producto_crear(request):
    if not request.user.perfil.es_artesano():
        messages.error(request, "No tienes permiso para esto.")
        return redirect("Home")

    if request.method == "POST":
        form = FormularioProducto(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.artesano = request.user
            producto.save()
            form.save_m2m()
            success_message = f'"{producto.nombre}" publicado correctamente.'

            if _is_ajax(request):
                return JsonResponse(
                    {
                        "ok": True,
                        "message": success_message,
                        "redirect": "/cuentas/dashboard/",
                        "producto": _producto_payload(producto, request),
                    }
                )

            messages.success(request, success_message)
            return redirect("cuentas:dashboard_artesano")
        if _is_ajax(request):
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Revisa la información del producto.",
                    "errors": _form_errors(form),
                },
                status=400,
            )
    else:
        form = FormularioProducto()

    return render(
        request,
        "cuentas/producto_form.html",
        {
            "form": form,
            "titulo": "Nuevo Producto",
            "boton": "Publicar producto",
            "modo_ajax": True,
        },
    )


@login_required
def producto_editar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, artesano=request.user)

    if request.method == "POST":
        form = FormularioProducto(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            success_message = f'"{producto.nombre}" actualizado correctamente.'

            if _is_ajax(request):
                return JsonResponse(
                    {
                        "ok": True,
                        "message": success_message,
                        "redirect": "/cuentas/dashboard/",
                        "producto": _producto_payload(producto, request),
                    }
                )

            messages.success(request, success_message)
            return redirect("cuentas:dashboard_artesano")
        if _is_ajax(request):
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Revisa la información del producto.",
                    "errors": _form_errors(form),
                },
                status=400,
            )
    else:
        form = FormularioProducto(instance=producto)

    return render(
        request,
        "cuentas/producto_form.html",
        {
            "form": form,
            "titulo": "Editar Producto",
            "boton": "Guardar cambios",
            "producto": producto,
            "modo_ajax": True,
        },
    )


@login_required
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, artesano=request.user)

    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        success_message = f'"{nombre}" eliminado correctamente.'

        if _is_ajax(request):
            productos = (
                Producto.objects.filter(artesano=request.user)
                .select_related("region")
                .prefetch_related("categorias")
                .order_by("-created")
            )
            stats = _dashboard_stats(productos)
            return JsonResponse(
                {
                    "ok": True,
                    "message": success_message,
                    "producto_id": producto_id,
                    "stats": stats,
                    "html_vacio": render_to_string(
                        "cuentas/partials/dashboard_empty.html",
                        request=request,
                    ),
                }
            )

        messages.success(request, success_message)
        return redirect("cuentas:dashboard_artesano")

    return render(
        request,
        "cuentas/producto_confirmar_eliminar.html",
        {"producto": producto},
    )
