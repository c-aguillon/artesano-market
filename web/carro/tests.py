from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Categoria, Producto, Region


class CarroViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="comprador", password="secret123")
        artesano = User.objects.create_user(username="art", password="secret123")
        region = Region.objects.create(nombre="Chiapas")
        categoria = Categoria.objects.create(nombre="Textil")
        self.producto = Producto.objects.create(
            nombre="Blusa bordada",
            descripcion="Detalle artesanal",
            precio="150.00",
            stock=1,
            artesano=artesano,
            region=region,
        )
        self.producto.categorias.add(categoria)
        self.client.login(username="comprador", password="secret123")

    def test_agregar_producto_respeta_stock_maximo(self):
        url = reverse("carro:agregar", args=[self.producto.id])

        first_response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        second_response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 400)
        self.assertIn("stock disponible", second_response.json()["message"])

    def test_limpiar_carro_vacia_sesion(self):
        self.client.get(reverse("carro:agregar", args=[self.producto.id]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        response = self.client.get(reverse("carro:limpiar"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_sincronizar_carro_reemplaza_desde_payload(self):
        response = self.client.post(
            reverse("carro:sincronizar"),
            data='{"items":[{"producto_id": %s, "cantidad": 1}]}' % self.producto.id,
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
