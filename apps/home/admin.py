from django.contrib import admin
from .models import Banner, HomeSeccion, Beneficio, HomeEditorial, HomeColeccion


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'orden', 'activo']
    list_editable = ['orden', 'activo']
    list_filter = ['activo']
    search_fields = ['titulo', 'subtitulo']

    fieldsets = (
        ('Contenido', {
            'fields': ('titulo', 'subtitulo', 'texto_boton', 'link')
        }),
        ('Imágenes', {
            'fields': ('imagen', 'imagen_movil'),
            'description': 'Sube la imagen para escritorio. La imagen móvil es opcional; si se deja vacía, se mostrará la de escritorio en todos los dispositivos.'
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
    )


class BeneficioInline(admin.TabularInline):
    model = Beneficio
    extra = 0
    fields = ('icono', 'titulo', 'texto', 'orden', 'activo')


class HomeEditorialInline(admin.TabularInline):
    model = HomeEditorial
    extra = 0
    fields = ('titulo', 'subtitulo', 'imagen', 'imagen_movil', 'texto_boton', 'enlace', 'orden', 'activo')


class HomeColeccionInline(admin.TabularInline):
    model = HomeColeccion
    extra = 0
    fields = ('titulo', 'descripcion', 'imagen', 'enlace', 'texto_boton', 'orden', 'activo')


@admin.register(HomeSeccion)
class HomeSeccionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'titulo', 'layout', 'orden', 'limite', 'activo')
    list_editable = ('titulo', 'layout', 'orden', 'limite', 'activo')
    list_display_links = ('tipo',)
    list_filter = ('activo', 'tipo')
    inlines = [BeneficioInline, HomeEditorialInline, HomeColeccionInline]

    fieldsets = (
        ('Contenido', {
            'fields': ('tipo', 'titulo', 'subtitulo', 'limite')
        }),
        ('Presentación visual', {
            'fields': ('layout',),
            'description': 'El layout determina cómo se muestra la sección. Si se deja vacío, se usa el layout por defecto del tipo (p. ej. destacados → carrusel, más vendidos → ranking, nuevos → editorial, ofertas → promo).'
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
    )


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'titulo', 'icono', 'orden', 'activo')
    list_editable = ('titulo', 'icono', 'orden', 'activo')
    list_filter = ('seccion', 'activo')
    search_fields = ('titulo', 'texto')


@admin.register(HomeEditorial)
class HomeEditorialAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'titulo', 'orden', 'activo')
    list_editable = ('titulo', 'orden', 'activo')
    list_filter = ('seccion', 'activo')
    search_fields = ('titulo', 'subtitulo')


@admin.register(HomeColeccion)
class HomeColeccionAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'titulo', 'orden', 'activo')
    list_editable = ('titulo', 'orden', 'activo')
    list_filter = ('seccion', 'activo')
    search_fields = ('titulo', 'descripcion')
