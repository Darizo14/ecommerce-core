from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Producto
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

    id_pedido = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='ID del Pedido'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos',
        blank=True,
        null=True
    )
    estado = models.CharField(
        max_length=20,
        default='pendiente'
    )
    metodo_pago = models.CharField(
        max_length=20,
        default='efectivo'
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
        usuario_nombre = self.usuario.username if self.usuario else 'Invitado'
        return f"Pedido {self.id_pedido} - {usuario_nombre}"

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

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='direccion_envio'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='direcciones_envio',
        blank=True,
        null=True
    )
    nombre_completo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Cuba')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dirección de Envío'
        verbose_name_plural = 'Direcciones de Envío'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_completo} - {self.direccion}, {self.ciudad}"


class Pago(models.Model):
    """Modelo para almacenar información de pagos"""

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
        default='pendiente'
    )
    metodo_pago = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
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
