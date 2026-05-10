from django.contrib import admin
from .models import Producto, Categoria

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'activo', 'creado_en')                     #Mostrar campos en la lista de productos
    search_fields = ('nombre', )                                                            #Crea un campo de búsqueda por nombre
    list_filter = ('activo', )                                                              #Crea un filtro lateral para el campo activo
    prepopulated_fields = {'slug': ('nombre',)}                                             #Llena automáticamente el slug a partir del nombre


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}