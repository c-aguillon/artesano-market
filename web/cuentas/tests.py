from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CuentasAjaxTests(TestCase):
    def test_login_ajax_responde_redirect(self):
        User.objects.create_user(username="cliente", password="secret123")

        response = self.client.post(
            reverse("cuentas:login"),
            {
                "username": "cliente",
                "password": "secret123",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["redirect"], "/")

    def test_registro_ajax_devuelve_errores(self):
        response = self.client.post(
            reverse("cuentas:registro"),
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "password1": "123",
                "password2": "456",
                "rol": "comprador",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertIn("password2", response.json()["errors"])
