from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import FormularioContacto
from django.core.mail import EmailMessage


def contacto(request):
    formulario_contacto = FormularioContacto()
    return render(request, "contacto/contacto.html", {'formulario': formulario_contacto})


@require_POST
def contacto_enviar(request):
    """Endpoint AJAX — recibe el POST y devuelve JSON, sin redirección."""
    formulario = FormularioContacto(data=request.POST)

    if not formulario.is_valid():
        return JsonResponse({'ok': False, 'errores': formulario.errors}, status=400)

    nombre   = request.POST.get("nombre", "")
    email    = request.POST.get("email", "")
    contenido = request.POST.get("contenido", "")

    email_mensaje = EmailMessage(
        "Mensaje de Artesano Market",
        f"Usuario: {nombre}\nCorreo: {email}\n\nEscribió:\n\n{contenido}",
        "",
        ["tapiar349@gmail.com"],
        reply_to=[email]
    )

    try:
        email_mensaje.send()
        return JsonResponse({'ok': True, 'mensaje': '¡Mensaje enviado con éxito! Te contactaremos pronto.'})
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return JsonResponse({'ok': False, 'mensaje': 'Ups, algo salió mal. Por favor intenta de nuevo.'}, status=500)