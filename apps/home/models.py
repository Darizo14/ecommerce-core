from django.db import models

class Banner(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título', blank=True)
    subtitulo = models.CharField(max_length=300, verbose_name='Subtítulo', blank=True)
    imagen = models.ImageField(upload_to='banner/', verbose_name='Imagen (Escritorio)')
    imagen_movil = models.ImageField(upload_to='banner/', verbose_name='Imagen (Móvil)', blank=True, null=True, help_text='Versión del banner para dispositivos móviles. Si se deja vacía, se usará la imagen de escritorio.')
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


class HomeSeccion(models.Model):
    """Sección configurable del Home (título, orden, visibilidad y contenido)."""

    TIPO_CATEGORIAS = 'categorias'
    TIPO_DESTACADOS = 'destacados'
    TIPO_MAS_VENDIDOS = 'mas_vendidos'
    TIPO_OFERTAS = 'ofertas'
    TIPO_NUEVOS = 'nuevos'
    TIPO_BENEFICIOS = 'beneficios'

    TIPOS = [
        (TIPO_CATEGORIAS, 'Categorías destacadas'),
        (TIPO_DESTACADOS, 'Productos destacados'),
        (TIPO_MAS_VENDIDOS, 'Productos más vendidos'),
        (TIPO_OFERTAS, 'Ofertas especiales'),
        (TIPO_NUEVOS, 'Productos nuevos'),
        (TIPO_BENEFICIOS, 'Beneficios de la tienda'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS, unique=True, verbose_name='Tipo de sección')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden', help_text='Menor número = aparece antes')
    limite = models.PositiveIntegerField(default=8, verbose_name='Límite', help_text='Cantidad máxima de productos o categorías a mostrar')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Sección del Home'
        verbose_name_plural = 'Secciones del Home'
        ordering = ['orden']

    def __str__(self):
        return self.titulo

    @property
    def beneficios_activos(self):
        return self.beneficios.filter(activo=True).order_by('orden')


class Beneficio(models.Model):
    """Beneficio mostrado en la sección de beneficios del Home."""

    ICONO_SEGURO = 'seguro'
    ICONO_ENVIO = 'envio'
    ICONO_GARANTIA = 'garantia'
    ICONO_ATENCION = 'atencion'
    ICONO_VERIFICADO = 'verificado'
    ICONO_COMPRA = 'compra'
    ICONO_REEMBOLSO = 'reembolso'
    ICONO_SOPORTE = 'soporte'

    ICONOS = [
        (ICONO_SEGURO, 'Pago seguro'),
        (ICONO_ENVIO, 'Envío rápido'),
        (ICONO_GARANTIA, 'Garantía de calidad'),
        (ICONO_ATENCION, 'Atención al cliente'),
        (ICONO_VERIFICADO, 'Productos verificados'),
        (ICONO_COMPRA, 'Compra sencilla'),
        (ICONO_REEMBOLSO, 'Reembolso garantizado'),
        (ICONO_SOPORTE, 'Soporte 24/7'),
    ]

    seccion = models.ForeignKey(
        HomeSeccion,
        on_delete=models.CASCADE,
        related_name='beneficios',
        verbose_name='Sección',
    )
    icono = models.CharField(max_length=30, choices=ICONOS, default=ICONO_SEGURO, verbose_name='Icono')
    titulo = models.CharField(max_length=120, verbose_name='Título')
    texto = models.TextField(blank=True, verbose_name='Descripción')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Beneficio'
        verbose_name_plural = 'Beneficios'
        ordering = ['orden']

    def __str__(self):
        return self.titulo
