from django.contrib import admin
from .models import Banner, HomeSeccion, Beneficio

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


@admin.register(HomeSeccion)
class HomeSeccionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'titulo', 'orden', 'limite', 'activo')
    list_editable = ('titulo', 'orden', 'limite', 'activo')
    list_display_links = ('tipo',)
    inlines = [BeneficioInline]


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'titulo', 'icono', 'orden', 'activo')
    list_editable = ('titulo', 'icono', 'orden', 'activo')
    list_filter = ('seccion', 'activo')
    search_fields = ('titulo', 'texto')
