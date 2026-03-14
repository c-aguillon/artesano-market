from django.shortcuts import render, redirect
from .forms import FormularioContacto
from django.core.mail import EmailMessage
from django.contrib import messages
from django.urls import reverse

# Create your views here.
def contacto(request):
    formulario_contacto = FormularioContacto()

    if request.method == "POST":
        formulario_contacto = FormularioContacto(data=request.POST)
        if formulario_contacto.is_valid():
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            contenido = request.POST.get("contenido")

            email_mensaje = EmailMessage(
                "Mensaje de Artesano Market",
                f"Usuario: {nombre}\nCorreo: {email}\n\nEscribió:\n\n{contenido}",
                "", # El correo que envía (configurado en settings)
                ["tapiar349@gmail.com"], # TU CORREO REAL
                reply_to=[email]
            )

            try:
                email_mensaje.send()
                # Redirigir con parámetro de éxito usando el nombre de la URL
                return redirect("/contacto/?valido")
            except Exception as e:
                print(f"Error enviando correo: {e}")
                return redirect("/contacto/?error")

    return render(request, "contacto/contacto.html", {'formulario': formulario_contacto})