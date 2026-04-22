from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from blog.models import Producto

from .models import Perfil


class FormularioRegistro(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirma tu contraseña",
                "autocomplete": "new-password",
            }
        ),
    )
    rol = forms.ChoiceField(
        choices=Perfil.ROL_CHOICES,
        label="¿Cómo quieres usar la plataforma?",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Usuario",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Correo electrónico",
                    "autocomplete": "email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido",
                    "autocomplete": "family-name",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        user = User(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
        )
        validate_password(password2, user=user)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.perfil.rol = self.cleaned_data["rol"]
            user.perfil.save()
        return user


class FormularioLogin(forms.Form):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Usuario",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "autocomplete": "current-password",
            }
        ),
    )


class FormularioProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "precio", "stock", "imagen", "categorias", "region"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del producto",
                    "maxlength": 200,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe tu producto...",
                }
            ),
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control border-left-0",
                    "placeholder": "0.00",
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1",
                    "min": "0",
                    "step": "1",
                    "inputmode": "numeric",
                }
            ),
            "imagen": forms.ClearableFileInput(
                attrs={
                    "class": "form-control-file",
                    "accept": "image/*",
                }
            ),
            "categorias": forms.CheckboxSelectMultiple(),
            "region": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

    def clean_categorias(self):
        categorias = self.cleaned_data["categorias"]
        if not categorias:
            raise forms.ValidationError("Selecciona al menos una categoría.")
        return categorias
