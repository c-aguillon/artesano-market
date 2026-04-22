from django.test import TestCase
from django.urls import reverse


class PwaViewsTests(TestCase):
    def test_manifest_exposes_install_metadata(self):
        response = self.client.get(reverse("manifest"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["short_name"], "Artesano")
        self.assertIn("icons", payload)

    def test_offline_page_renders(self):
        response = self.client.get(reverse("offline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin conexión")
