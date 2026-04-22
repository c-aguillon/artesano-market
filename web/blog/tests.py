from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto, Region


class BlogViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="artesano", password="secret123")
        self.region = Region.objects.create(nombre="Oaxaca")
        self.categoria = Categoria.objects.create(nombre="Barro")
        self.producto = Producto.objects.create(
            nombre="Jarrón artesanal",
            descripcion="Hecho a mano",
            precio="299.00",
            stock=4,
            artesano=self.user,
            region=self.region,
        )
        self.producto.categorias.add(self.categoria)

    def test_catalogo_responde_json_para_ajax(self):
        response = self.client.get(
            reverse("Blog"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["productos"]), 1)
        self.assertEqual(payload["productos"][0]["nombre"], "Jarrón artesanal")

    def test_catalogo_filtra_por_region(self):
        response = self.client.get(reverse("Blog"), {"region": self.region.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jarrón artesanal")
