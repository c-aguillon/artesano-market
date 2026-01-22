from django.contrib import admin
from .models import Categoria, Producto, Region

# Configuración opcional para ver columnas en el admin
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'artesano', 'region')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('region', 'categorias')
    readonly_fields = ('created', 'updated')

class CategoriaAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

class RegionAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

# Registro de modelos
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Region, RegionAdmin)