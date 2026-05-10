from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Producto
from django.utils.text import slugify
import uuid


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    precio_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='municipios')
    nombre = models.CharField(max_length=100)
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Reparto(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='repartos')
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Reparto'
        verbose_name_plural = 'Repartos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tienda'
        verbose_name_plural = 'Tiendas'

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    """Modelo para almacenar información de pedidos"""
    
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('devuelto', 'Devuelto'),
    )
    
    METODO_PAGO_CHOICES = (
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Contra Reembolso'),
    )
    
    id_pedido = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='ID del Pedido'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='tarjeta'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        indexes = [
            models.Index(fields=['usuario', '-fecha_creacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['id_pedido']),
        ]

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.usuario.username}"

    def calcular_total(self):
        """Calcula el total del pedido"""
        self.total = self.subtotal + self.costo_envio
        return self.total


class LineaPedido(models.Model):
    """Modelo para cada producto en un pedido"""
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='lineas'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='lineas_pedido'
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Línea de Pedido'
        verbose_name_plural = 'Líneas de Pedidos'
        unique_together = ['pedido', 'producto']

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        """Calcula el subtotal de la línea"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class DireccionEnvio(models.Model):
    """Modelo para almacenar direcciones de envío"""
    
    TIPO_DOMICILIO_CHOICES = (
        ('casa', 'Casa'),
        ('oficina', 'Oficina'),
        ('otro', 'Otro'),
    )
    
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='direccion_envio'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='direcciones_envio'
    )
    nombre_completo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    numero = models.CharField(max_length=20, verbose_name='Número/Apto')
    complemento = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Complemento (referencia)'
    )
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    pais = models.CharField(max_length=100, default='Argentina')
    tipo_domicilio = models.CharField(
        max_length=20,
        choices=TIPO_DOMICILIO_CHOICES,
        default='casa'
    )
    es_direccion_predeterminada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dirección de Envío'
        verbose_name_plural = 'Direcciones de Envío'
        ordering = ['-es_direccion_predeterminada', '-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_completo} - {self.direccion}, {self.ciudad}"

    def save(self, *args, **kwargs):
        """Si se marca como predeterminada, desactiva las demás"""
        if self.es_direccion_predeterminada:
            DireccionEnvio.objects.filter(
                usuario=self.usuario,
                es_direccion_predeterminada=True
            ).exclude(pk=self.pk).update(es_direccion_predeterminada=False)
        super().save(*args, **kwargs)


class Pago(models.Model):
    """Modelo para almacenar información de pagos"""
    
    ESTADO_PAGO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    )
    
    id_transaccion = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='ID de Transacción'
    )
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='pago'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default='pendiente'
    )
    metodo_pago = models.CharField(max_length=50)
    referencia_pago = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Referencia del Pago'
    )
    descripcion_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción de Error'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['id_transaccion']),
        ]

    def __str__(self):
        return f"Pago {self.id_transaccion} - {self.estado}"
