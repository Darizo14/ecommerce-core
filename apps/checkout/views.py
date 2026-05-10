from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Pedido, LineaPedido, DireccionEnvio, Pago, Provincia, Municipio, Reparto, Tienda
from apps.products.models import Producto


@login_required
def confirmacion_pedido(request, pedido_id):
    """
    Vista para mostrar confirmación del pedido creado
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
        'lineas': pedido.lineas.all(),
        'direccion': pedido.direccion_envio,
        'pago': pedido.pago,
    }
    
    return render(request, 'checkout/confirmacion_pedido.html', context)


@login_required
def proceso_checkout(request):
    """
    Vista para el checkout paso a paso
    """
    from django.http import JsonResponse
    
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito:vista_carrito')
    
    productos = []
    subtotal = Decimal('0.00')
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            precio = producto.precio
            subtotal_item = cantidad * precio
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal_item
            })
            subtotal += subtotal_item
        except Producto.DoesNotExist:
            continue
    
    accion = request.POST.get('accion', '')
    
    if request.method == 'POST':
        paso_actual = int(request.POST.get('paso', 1))
        checkout_data = request.session.get('checkout_data', {})
        
        if paso_actual == 1 and accion == 'siguiente':
            checkout_data['nombre'] = request.POST.get('nombre', '')
            checkout_data['telefono'] = request.POST.get('telefono', '')
            paso = 2
        elif paso_actual == 2 and accion == 'siguiente':
            checkout_data['metodo_entrega'] = request.POST.get('metodo_entrega', '')
            if checkout_data['metodo_entrega'] == 'mensajeria':
                checkout_data['provincia_id'] = request.POST.get('provincia', '')
                checkout_data['municipio_id'] = request.POST.get('municipio', '')
                checkout_data['reparto_id'] = request.POST.get('reparto', '')
                checkout_data['direccion'] = request.POST.get('direccion', '')
                
                if checkout_data['provincia_id']:
                    try:
                        provincia = Provincia.objects.get(id=checkout_data['provincia_id'])
                        checkout_data['provincia_nombre'] = provincia.nombre
                        checkout_data['precio_envio'] = float(provincia.precio_envio)
                    except Provincia.DoesNotExist:
                        pass
                
                if checkout_data['municipio_id']:
                    try:
                        municipio = Municipio.objects.get(id=checkout_data['municipio_id'])
                        checkout_data['municipio_nombre'] = municipio.nombre
                        checkout_data['precio_envio'] += float(municipio.precio_adicional)
                    except Municipio.DoesNotExist:
                        pass
                
                if checkout_data['reparto_id']:
                    try:
                        reparto = Reparto.objects.get(id=checkout_data['reparto_id'])
                        checkout_data['reparto_nombre'] = reparto.nombre
                    except Reparto.DoesNotExist:
                        pass
            elif checkout_data['metodo_entrega'] == 'tienda':
                checkout_data['provincia_id'] = ''
                checkout_data['municipio_id'] = ''
                checkout_data['reparto_id'] = ''
                checkout_data['direccion'] = ''
                checkout_data['precio_envio'] = 0
            paso = 3
        elif paso_actual == 3 and accion == 'siguiente':
            checkout_data['metodo_pago'] = 'efectivo'
            paso = 4
        elif accion == 'atras':
            paso = max(1, paso_actual - 1)
        else:
            paso = 1
    else:
        checkout_data = {}
        paso = 1
    
    request.session['checkout_data'] = checkout_data
    
    if request.method == 'POST':
        if paso == 1:
            checkout_data['nombre'] = request.POST.get('nombre', '')
            checkout_data['telefono'] = request.POST.get('telefono', '')
        elif paso == 2:
            checkout_data['metodo_entrega'] = request.POST.get('metodo_entrega', '')
            if checkout_data['metodo_entrega'] == 'mensajeria':
                checkout_data['provincia_id'] = request.POST.get('provincia', '')
                checkout_data['municipio_id'] = request.POST.get('municipio', '')
                checkout_data['reparto_id'] = request.POST.get('reparto', '')
                checkout_data['direccion'] = request.POST.get('direccion', '')
                
                if checkout_data['provincia_id']:
                    try:
                        provincia = Provincia.objects.get(id=checkout_data['provincia_id'])
                        checkout_data['provincia_nombre'] = provincia.nombre
                        checkout_data['precio_envio'] = float(provincia.precio_envio)
                    except Provincia.DoesNotExist:
                        pass
                
                if checkout_data['municipio_id']:
                    try:
                        municipio = Municipio.objects.get(id=checkout_data['municipio_id'])
                        checkout_data['municipio_nombre'] = municipio.nombre
                        checkout_data['precio_envio'] += float(municipio.precio_adicional)
                    except Municipio.DoesNotExist:
                        pass
                
                if checkout_data['reparto_id']:
                    try:
                        reparto = Reparto.objects.get(id=checkout_data['reparto_id'])
                        checkout_data['reparto_nombre'] = reparto.nombre
                    except Reparto.DoesNotExist:
                        pass
            elif checkout_data['metodo_entrega'] == 'tienda':
                checkout_data['provincia_id'] = ''
                checkout_data['municipio_id'] = ''
                checkout_data['reparto_id'] = ''
                checkout_data['direccion'] = ''
                checkout_data['precio_envio'] = 0
        elif paso == 3:
            checkout_data['metodo_pago'] = request.POST.get('metodo_pago', 'efectivo')
        
        request.session['checkout_data'] = checkout_data
    
    if accion == 'confirmar':
        return crear_pedido_checkout(request, productos, subtotal, checkout_data)
    
    precio_envio = checkout_data.get('precio_envio', 0)
    total = subtotal + Decimal(str(precio_envio))
    
    provincia_id = checkout_data.get('provincia_id', '')
    municipio_id = checkout_data.get('municipio_id', '')
    reparto_id = checkout_data.get('reparto_id', '')
    
    provincias = Provincia.objects.all().order_by('nombre')
    municipios = []
    repartos = []
    
    if provincia_id:
        try:
            provincia = Provincia.objects.get(id=provincia_id)
            municipios = provincia.municipios.all().order_by('nombre')
        except Provincia.DoesNotExist:
            pass
    
    if municipio_id:
        try:
            municipio = Municipio.objects.get(id=municipio_id)
            repartos = municipio.repartos.all().order_by('nombre')
        except Municipio.DoesNotExist:
            pass
    
    tienda = Tienda.objects.filter(activa=True).first()
    
    context = {
        'paso': paso,
        'productos': productos,
        'subtotal': subtotal,
        'precio_envio': precio_envio,
        'total': total,
        'checkout_data': checkout_data,
        'provincias': provincias,
        'municipios': municipios,
        'repartos': repartos,
        'tienda': tienda,
    }
    
    return render(request, 'checkout/checkout_paso_a_paso.html', context)


@login_required
def crear_pedido_checkout(request, productos, subtotal, checkout_data):
    """
    Crea el pedido a partir de los datos del checkout paso a paso
    """
    from django.utils import timezone
    
    try:
        with transaction.atomic():
            precio_envio = checkout_data.get('precio_envio', 0)
            total = subtotal + Decimal(str(precio_envio))
            
            pedido = Pedido.objects.create(
                usuario=request.user,
                metodo_pago=checkout_data.get('metodo_pago', 'efectivo'),
                subtotal=subtotal,
                costo_envio=precio_envio,
                total=total,
                notas=f"Teléfono: {checkout_data.get('telefono', '')}"
            )
            
            for item in productos:
                LineaPedido.objects.create(
                    pedido=pedido,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal']
                )
            
            metodo_entrega = checkout_data.get('metodo_entrega', 'tienda')
            
            if metodo_entrega == 'mensajeria':
                direccion = DireccionEnvio.objects.create(
                    pedido=pedido,
                    usuario=request.user,
                    nombre_completo=checkout_data.get('nombre', ''),
                    telefono=checkout_data.get('telefono', ''),
                    direccion=checkout_data.get('direccion', ''),
                    ciudad=checkout_data.get('reparto_nombre', ''),
                    provincia=checkout_data.get('provincia_nombre', ''),
                    codigo_postal='',
                    pais='Cuba',
                    tipo_domicilio='casa'
                )
            else:
                tienda = Tienda.objects.filter(activa=True).first()
                if tienda:
                    direccion = DireccionEnvio.objects.create(
                        pedido=pedido,
                        usuario=request.user,
                        nombre_completo=checkout_data.get('nombre', ''),
                        telefono=checkout_data.get('telefono', ''),
                        direccion=tienda.direccion,
                        ciudad='Recoger en tienda',
                        provincia='La Habana',
                        codigo_postal='',
                        pais='Cuba',
                        tipo_domicilio='tienda'
                    )
            
            Pago.objects.create(
                pedido=pedido,
                monto=total,
                metodo_pago=checkout_data.get('metodo_pago', 'efectivo'),
                estado='pendiente'
            )
            
            if 'carrito' in request.session:
                request.session['carrito'] = {}
            if 'checkout_data' in request.session:
                del request.session['checkout_data']
            
            messages.success(
                request,
                f'¡Pedido creado exitosamente! Tu número de pedido es: {pedido.id_pedido}'
            )
            
            return redirect('checkout:confirmacion', pedido_id=pedido.id)
    
    except Exception as e:
        messages.error(request, f'Error al crear el pedido: {str(e)}')
        return redirect('checkout:proceso_checkout')


def api_municipios(request):
    """
    API para obtener los municipios de una provincia
    """
    from django.http import JsonResponse
    
    provincia_id = request.GET.get('provincia_id')
    
    if not provincia_id:
        return JsonResponse({'municipios': []})
    
    try:
        provincia = Provincia.objects.get(id=provincia_id)
        municipios = provincia.municipios.all().order_by('nombre')
        
        data = {
            'municipios': [
                {
                    'id': m.id,
                    'nombre': m.nombre,
                    'precio_adicional': float(m.precio_adicional)
                }
                for m in municipios
            ]
        }
        
        return JsonResponse(data)
    except Provincia.DoesNotExist:
        return JsonResponse({'municipios': []})


def api_repartos(request):
    """
    API para obtener los repartos de un municipio
    """
    from django.http import JsonResponse
    
    municipio_id = request.GET.get('municipio_id')
    
    if not municipio_id:
        return JsonResponse({'repartos': []})
    
    try:
        municipio = Municipio.objects.get(id=municipio_id)
        repartos = municipio.repartos.all().order_by('nombre')
        
        data = {
            'repartos': [
                {
                    'id': r.id,
                    'nombre': r.nombre
                }
                for r in repartos
            ]
        }
        
        return JsonResponse(data)
    except Municipio.DoesNotExist:
        return JsonResponse({'repartos': []})
