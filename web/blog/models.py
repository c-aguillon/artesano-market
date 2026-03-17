from django.db import models
from django.contrib.auth.models import User

# Modelo para las Regiones (Estados de la República)
class Region(models.Model):
    nombre = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'región'
        verbose_name_plural = 'regiones'

    def __str__(self):
        return self.nombre

# Modelo para Categorías (Textiles, Barro, Joyería, etc.)
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre

# Modelo Principal: PRODUCTO (Antes Post)
class Producto(models.Model):
    nombre = models.CharField(max_length=200) # Antes titulo
    descripcion = models.TextField()          # Antes contenido (ahora permite textos largos)
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Nuevo: Precio
    stock = models.PositiveIntegerField(default=1)                # Nuevo: Inventario
    
    # Relaciones
    imagen = models.ImageField(upload_to='productos', null=True, blank=True)
    artesano = models.ForeignKey(User, on_delete=models.CASCADE) # El usuario que lo crea
    categorias = models.ManyToManyField(Categoria)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True) # Nuevo: Filtro por zona
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"