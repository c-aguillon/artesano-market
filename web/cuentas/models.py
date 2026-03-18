import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    ROL_CHOICES = [
        ('comprador', 'Comprador'),
        ('artesano', 'Artesano'),
    ]
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol     = models.CharField(max_length=20, choices=ROL_CHOICES, default='comprador')
    foto    = models.ImageField(upload_to='perfiles', null=True, blank=True)
    bio     = models.TextField(blank=True)
    carrito = models.TextField(default='{}')

    def get_carrito(self):
        return json.loads(self.carrito)

    def set_carrito(self, datos):
        self.carrito = json.dumps(datos)
        self.save()

    def es_artesano(self):
        return self.rol == 'artesano'

    def __str__(self):
        return f"{self.user.username} — {self.rol}"


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()