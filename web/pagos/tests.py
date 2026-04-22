from django.test import TestCase
from django.urls import reverse


class PagosViewTests(TestCase):
    def test_create_order_rechaza_carrito_vacio(self):
        response = self.client.post(reverse("paypal_api:create_order"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "El carrito está vacío")
