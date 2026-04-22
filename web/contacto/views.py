from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import FormularioContacto


def contacto(request):
    formulario_contacto = FormularioContacto()
    return render(request, "contacto/contacto.html", {"formulario": formulario_contacto})


@require_POST
def contacto_enviar(request):
    formulario = FormularioContacto(data=request.POST)

    if not formulario.is_valid():
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Por favor revisa los campos obligatorios.",
                "errores": formulario.errors,
            },
            status=400,
        )

    nombre = formulario.cleaned_data["nombre"]
    email = formulario.cleaned_data["email"]
    contenido = formulario.cleaned_data["contenido"]

    email_mensaje = EmailMessage(
        "Mensaje de Artesano Market",
        f"Usuario: {nombre}\nCorreo: {email}\n\nEscribió:\n\n{contenido}",
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        reply_to=[email],
    )

    try:
        email_mensaje.send()
        return JsonResponse(
            {
                "ok": True,
                "mensaje": "¡Mensaje enviado con éxito! Te contactaremos pronto.",
            }
        )
    except Exception:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Ups, algo salió mal. Por favor intenta de nuevo.",
            },
            status=500,
        )
