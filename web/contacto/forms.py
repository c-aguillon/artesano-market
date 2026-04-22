from django import forms


class FormularioContacto(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        required=True,
        max_length=120,
    )
    email = forms.EmailField(
        label="Email",
        required=True,
    )
    contenido = forms.CharField(
        label="Contenido",
        widget=forms.Textarea,
        required=True,
        max_length=2000,
    )
