from django.contrib import admin
from .models import Banner

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
