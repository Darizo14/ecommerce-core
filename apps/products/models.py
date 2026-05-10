from django.db import models
from django.utils.text import slugify

##############PRODUCTOS######################
class Producto(models.Model):
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.PROTECT,
        related_name='productos',
        null=True,
        blank=True
    )

    nombre = models.CharField(max_length=255)                           #Campos de la tabla producto
    imagen = models.ImageField(upload_to='products/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)                          #Para desactivar productos sin borrarlos
    creado_en = models.DateTimeField(auto_now_add=True)                 #Para ordenar por fecha de creación
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['activo']),
        ]

    def save(self, *args, **kwargs):                                    #Genera el slug automáticamente si no se ha proporcionado

        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1

            while Producto.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.nombre                                              #Muestra el nombre del producto en lugar de "Producto object (1)"

        

##############CATEGORIA######################
class Categoria(models.Model):
    nombre = models.CharField(max_length=255)                           #Campos para la tabla categoria
    slug = models.SlugField(unique=True, blank=True)

    padre = models.ForeignKey(   
        'self',                                                         #Apunta a la misma clase (Categoria)
        on_delete=models.PROTECT,                                       #Evita borrar una categoría si tiene subcategorías
        related_name='subcategorias',                                   #Permite acceder a hijos: categoria.subcategorias.all()
        null=True,                                                      #Puede no tener padre (categoría raíz)
        blank=True                                                      #Opcional en formularios
    )
    

    activo = models.BooleanField(default=True)                          #Permite desactivar categorías sin borrarlas

    class Meta:
        verbose_name_plural = "Categorías"
        indexes = [
            models.Index(fields=['slug']),
        ]


    def save(self, *args, **kwargs):                                    #Genera el slug automáticamente si no se ha proporcionado

        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1

            while Producto.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):                                                  #Define cómo se representa el objeto como texto                
        return self.nombre                                              #Muestra el nombre de la categoría en lugar de "Categoria object (1)"                