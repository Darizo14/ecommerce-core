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
    """Sección configurable del Home (título, orden, visibilidad y contenido).

    Separa QUÉ contenido muestra la sección (`tipo`) de CÓMO se presenta
    visualmente (`layout`). Ambos son configurables desde el Admin.
    """

    # --- Qué contenido muestra la sección ---
    TIPO_CATEGORIAS = 'categorias'
    TIPO_DESTACADOS = 'destacados'
    TIPO_MAS_VENDIDOS = 'mas_vendidos'
    TIPO_OFERTAS = 'ofertas'
    TIPO_NUEVOS = 'nuevos'
    TIPO_EDITORIAL = 'editorial'
    TIPO_COLECCIONES = 'colecciones'
    TIPO_BENEFICIOS = 'beneficios'

    TIPOS = [
        (TIPO_CATEGORIAS, 'Categorías destacadas'),
        (TIPO_DESTACADOS, 'Productos destacados'),
        (TIPO_MAS_VENDIDOS, 'Productos más vendidos'),
        (TIPO_OFERTAS, 'Ofertas especiales'),
        (TIPO_NUEVOS, 'Productos nuevos'),
        (TIPO_EDITORIAL, 'Bloque editorial'),
        (TIPO_COLECCIONES, 'Descubre / Inspiración'),
        (TIPO_BENEFICIOS, 'Beneficios de la tienda'),
    ]

    # --- Cómo se presenta visualmente ---
    LAYOUT_CAROUSEL = 'carousel'
    LAYOUT_GRID = 'grid'
    LAYOUT_RANKING = 'ranking'
    LAYOUT_EDITORIAL = 'editorial'
    LAYOUT_PROMO = 'promo'
    LAYOUT_CATEGORIES = 'categories'
    LAYOUT_BENEFITS = 'benefits'

    # Layout por defecto de cada tipo (puede sobrescribirse en el Admin).
    LAYOUT_POR_TIPO = {
        TIPO_CATEGORIAS: LAYOUT_CATEGORIES,
        TIPO_DESTACADOS: LAYOUT_CAROUSEL,
        TIPO_MAS_VENDIDOS: LAYOUT_RANKING,
        TIPO_OFERTAS: LAYOUT_PROMO,
        TIPO_NUEVOS: LAYOUT_EDITORIAL,
        TIPO_EDITORIAL: LAYOUT_EDITORIAL,
        TIPO_COLECCIONES: LAYOUT_GRID,
        TIPO_BENEFICIOS: LAYOUT_BENEFITS,
    }

    LAYOUTS = [
        (LAYOUT_CAROUSEL, 'Carrusel horizontal'),
        (LAYOUT_GRID, 'Cuadrícula'),
        (LAYOUT_RANKING, 'Ranking numerado'),
        (LAYOUT_EDITORIAL, 'Editorial / asimétrico'),
        (LAYOUT_PROMO, 'Bloque promocional'),
        (LAYOUT_CATEGORIES, 'Categorías circulares'),
        (LAYOUT_BENEFITS, 'Beneficios (iconos)'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS, unique=True, verbose_name='Tipo de sección')
    layout = models.CharField(
        max_length=20, choices=LAYOUTS, blank=True,
        verbose_name='Layout (presentación)',
        help_text='Cómo se presenta visualmente la sección. Si se deja vacío se usa el layout por defecto del tipo.',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    subtitulo = models.CharField(max_length=300, verbose_name='Subtítulo', blank=True, help_text='Texto secundario que acompaña al título (opcional).')
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
    def layout_efectivo(self):
        """Devuelve el layout a usar: el explícito o el por defecto del tipo."""
        return self.layout or self.LAYOUT_POR_TIPO.get(self.tipo, self.LAYOUT_GRID)

    @property
    def beneficios_activos(self):
        return self.beneficios.filter(activo=True).order_by('orden')

    @property
    def editoriales_activas(self):
        return self.editoriales.filter(activo=True).order_by('orden')

    @property
    def colecciones_activas(self):
        return self.colecciones.filter(activo=True).order_by('orden')


class HomeEditorial(models.Model):
    """Bloque editorial tipo revista, configurable desde el Admin.

    Pertenece a una sección `HomeSeccion` de tipo `editorial`.
    """

    seccion = models.ForeignKey(
        HomeSeccion,
        on_delete=models.CASCADE,
        related_name='editoriales',
        verbose_name='Sección',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    subtitulo = models.CharField(max_length=300, verbose_name='Subtítulo', blank=True)
    imagen = models.ImageField(upload_to='home-editorial/', verbose_name='Imagen (Escritorio)')
    imagen_movil = models.ImageField(upload_to='home-editorial/', verbose_name='Imagen (Móvil)', blank=True, null=True, help_text='Versión para móviles. Si se deja vacía se usará la de escritorio.')
    texto_boton = models.CharField(max_length=100, verbose_name='Texto del botón', blank=True, default='Descubrir')
    enlace = models.CharField(max_length=500, verbose_name='Enlace', blank=True, help_text='URL a la que apunta el botón')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Bloque editorial'
        verbose_name_plural = 'Bloques editoriales'
        ordering = ['orden']

    def __str__(self):
        return self.titulo


class HomeColeccion(models.Model):
    """Bloque de inspiración/descubrimiento del Home (Descubre).

    Pertenece a una sección `HomeSeccion` de tipo `colecciones`.
    Cada bloque muestra una imagen, un título y un enlace hacia una
    categoría o listado.
    """

    seccion = models.ForeignKey(
        HomeSeccion,
        on_delete=models.CASCADE,
        related_name='colecciones',
        verbose_name='Sección',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.CharField(max_length=300, verbose_name='Descripción', blank=True)
    imagen = models.ImageField(upload_to='home-colecciones/', verbose_name='Imagen')
    enlace = models.CharField(max_length=500, verbose_name='Enlace', blank=True, help_text='URL al que apunta el bloque')
    texto_boton = models.CharField(max_length=100, verbose_name='Texto del botón', blank=True, default='Descubrir')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Bloque de inspiración'
        verbose_name_plural = 'Bloques de inspiración'
        ordering = ['orden']

    def __str__(self):
        return self.titulo


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
