from django.contrib import admin
from .models import Producto, Categoria, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('imagen', 'orden')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'precio_oferta', 'en_oferta', 'destacado', 'orden_destacado', 'stock', 'total_vendido', 'activo', 'creado_en')
    list_editable = ('destacado', 'orden_destacado')
    search_fields = ('nombre',)
    list_filter = ('activo', 'en_oferta', 'destacado', 'categoria')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ProductImageInline]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}