from django.contrib import admin
from django.utils.html import format_html
from .models import Pedido, LineaPedido, DireccionEnvio, Pago, Provincia, Municipio, Reparto, Tienda


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_envio')
    search_fields = ('nombre',)


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia', 'precio_adicional')
    list_filter = ('provincia',)
    search_fields = ('nombre',)


@admin.register(Reparto)
class RepartoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'municipio')
    list_filter = ('municipio__provincia',)
    search_fields = ('nombre',)


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'activa')
    list_filter = ('activa',)


class LineaPedidoInline(admin.TabularInline):
    """Muestra líneas de pedido dentro de la vista de Pedido"""
    model = LineaPedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_creacion')
    can_delete = False
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')


class DireccionEnvioInline(admin.StackedInline):
    """Muestra dirección de envío dentro de la vista de Pedido"""
    model = DireccionEnvio
    extra = 0
    readonly_fields = ('fecha_creacion',)
    can_delete = False


class PagoInline(admin.StackedInline):
    """Muestra información de pago dentro de la vista de Pedido"""
    model = Pago
    extra = 0
    readonly_fields = ('id_transaccion', 'fecha_creacion', 'fecha_actualizacion')
    can_delete = False
    fields = ('id_transaccion', 'monto', 'estado', 'metodo_pago', 'fecha_creacion')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Configuración del admin para Pedidos"""
    
    list_display = (
        'id_pedido',
        'usuario',
        'estado_badge',
        'metodo_pago',
        'total_formateado',
        'fecha_creacion',
    )
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('id_pedido', 'usuario__username', 'usuario__email')
    readonly_fields = (
        'id_pedido',
        'usuario',
        'fecha_creacion',
        'fecha_actualizacion',
        'subtotal',
        'costo_envio',
        'total',
    )
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id_pedido', 'usuario', 'estado', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Detalles Económicos', {
            'fields': ('subtotal', 'costo_envio', 'total')
        }),
        ('Pago', {
            'fields': ('metodo_pago',)
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LineaPedidoInline, DireccionEnvioInline, PagoInline]
    
    def estado_badge(self, obj):
        """Muestra un badge con el estado del pedido"""
        color = '#FFC107'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    def total_formateado(self, obj):
        """Muestra el total formateado"""
        return f"${obj.total:.2f}"
    total_formateado.short_description = 'Total'
    
    def has_add_permission(self, request):
        """Los pedidos no se crean desde el admin"""
        return False


@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    """Configuración del admin para Direcciones de Envío"""
    
    list_display = (
        'nombre_completo',
        'ciudad',
        'provincia',
        'usuario',
        'fecha_creacion',
    )
    list_filter = ('ciudad', 'provincia')
    search_fields = ('nombre_completo', 'usuario__username', 'ciudad')
    readonly_fields = ('fecha_creacion', 'usuario')
    
    fieldsets = (
        ('Información de Contacto', {
            'fields': ('usuario', 'nombre_completo', 'telefono')
        }),
        ('Dirección', {
            'fields': (
                'direccion',
                ('ciudad', 'provincia'),
                'pais',
            )
        }),
        ('Información del Sistema', {
            'fields': ('pedido', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Las direcciones se crean desde el checkout"""
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Configuración del admin para Pagos"""
    
    list_display = (
        'id_transaccion',
        'pedido',
        'monto_formateado',
        'estado',
        'metodo_pago',
        'fecha_creacion',
    )
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('id_transaccion', 'pedido__id_pedido')
    readonly_fields = (
        'id_transaccion',
        'pedido',
        'fecha_creacion',
        'fecha_actualizacion',
    )
    
    fieldsets = (
        ('Información de Transacción', {
            'fields': ('id_transaccion', 'pedido', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Detalles del Pago', {
            'fields': ('monto', 'estado', 'metodo_pago')
        }),
    )
    
    def monto_formateado(self, obj):
        """Muestra el monto formateado"""
        return f"${obj.monto:.2f}"
    monto_formateado.short_description = 'Monto'
    
    def has_add_permission(self, request):
        """Los pagos se crean automáticamente"""
        return False


@admin.register(LineaPedido)
class LineaPedidoAdmin(admin.ModelAdmin):
    """Configuración del admin para Líneas de Pedido"""
    
    list_display = (
        'producto',
        'pedido',
        'cantidad',
        'precio_unitario',
        'subtotal_formateado',
        'fecha_creacion',
    )
    list_filter = ('fecha_creacion', 'pedido__estado')
    search_fields = ('producto__nombre', 'pedido__id_pedido')
    readonly_fields = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_creacion')
    
    def has_add_permission(self, request):
        """Las líneas se crean automáticamente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def subtotal_formateado(self, obj):
        """Muestra el subtotal formateado"""
        return f"${obj.subtotal:.2f}"
    subtotal_formateado.short_description = 'Subtotal'
