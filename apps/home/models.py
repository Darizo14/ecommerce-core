from django.db import models

class Banner(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título', blank=True)
    subtitulo = models.CharField(max_length=300, verbose_name='Subtítulo', blank=True)
    imagen = models.ImageField(upload_to='banner/', verbose_name='Imagen')
    link = models.CharField(max_length=500, verbose_name='Enlace', blank=True, help_text='URL a la que apunta el botón')
    texto_boton = models.CharField(max_length=100, verbose_name='Texto del botón', blank=True, default='Ver más')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['orden']

    def __str__(self):
        return self.titulo
