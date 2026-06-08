from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from .models import Pedido, LineaPedido, DireccionEnvio, Pago, Provincia, Municipio, Reparto, Tienda
from apps.products.models import Producto


def confirmacion_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    direccion = getattr(pedido, 'direccion_envio', None)
    pago = getattr(pedido, 'pago', None)

    context = {
        'pedido': pedido,
        'lineas': pedido.lineas.all(),
        'direccion': direccion,
        'pago': pago,
    }
    return render(request, 'checkout/confirmacion_pedido.html', context)


def proceso_checkout(request):
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
                'subtotal': subtotal_item,
            })
            subtotal += subtotal_item
        except Producto.DoesNotExist:
            continue

    accion = request.POST.get('accion', '')

    if request.method == 'POST':
        checkout_data = request.session.get('checkout_data', {})

        if accion == 'confirmar':
            return crear_pedido_checkout(request, productos, subtotal, checkout_data)

        paso_actual = int(request.POST.get('paso', 1))

        if paso_actual == 1 and accion == 'siguiente':
            checkout_data.update(
                nombre=request.POST.get('nombre', ''),
                telefono=request.POST.get('telefono', ''),
            )
            paso = 2
        elif paso_actual == 2 and accion == 'siguiente':
            checkout_data['metodo_entrega'] = request.POST.get('metodo_entrega', '')
            if checkout_data['metodo_entrega'] == 'mensajeria':
                checkout_data['provincia_id'] = request.POST.get('provincia', '')
                checkout_data['municipio_id'] = request.POST.get('municipio', '')
                checkout_data['reparto_id'] = request.POST.get('reparto', '')
                checkout_data['direccion'] = request.POST.get('direccion', '')

                if checkout_data['provincia_id']:
                    provincia = Provincia.objects.filter(id=checkout_data['provincia_id']).first()
                    if provincia:
                        checkout_data['provincia_nombre'] = provincia.nombre
                        checkout_data['precio_envio'] = float(provincia.precio_envio)

                if checkout_data['municipio_id']:
                    municipio = Municipio.objects.filter(id=checkout_data['municipio_id']).first()
                    if municipio:
                        checkout_data['municipio_nombre'] = municipio.nombre
                        checkout_data['precio_envio'] = checkout_data.get('precio_envio', 0) + float(municipio.precio_adicional)

                if checkout_data['reparto_id']:
                    reparto = Reparto.objects.filter(id=checkout_data['reparto_id']).first()
                    if reparto:
                        checkout_data['reparto_nombre'] = reparto.nombre
            else:
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

        request.session['checkout_data'] = checkout_data
    else:
        checkout_data = {}
        paso = 1

    precio_envio = checkout_data.get('precio_envio', 0)
    total = subtotal + Decimal(str(precio_envio))

    provincia_id = checkout_data.get('provincia_id', '')
    municipio_id = checkout_data.get('municipio_id', '')
    reparto_id = checkout_data.get('reparto_id', '')

    provincias = Provincia.objects.all().order_by('nombre')
    municipios = []
    repartos = []

    if provincia_id:
        provincia = Provincia.objects.filter(id=provincia_id).first()
        if provincia:
            municipios = provincia.municipios.all().order_by('nombre')

    if municipio_id:
        municipio = Municipio.objects.filter(id=municipio_id).first()
        if municipio:
            repartos = municipio.repartos.all().order_by('nombre')

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


def crear_pedido_checkout(request, productos, subtotal, checkout_data):
    try:
        with transaction.atomic():
            precio_envio = checkout_data.get('precio_envio', 0)
            total = subtotal + Decimal(str(precio_envio))

            pedido = Pedido.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                subtotal=subtotal,
                costo_envio=precio_envio,
                total=total,
                notas=f"Teléfono: {checkout_data.get('telefono', '')}",
            )

            for item in productos:
                LineaPedido.objects.create(
                    pedido=pedido,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal'],
                )
                producto = item['producto']
                producto.stock = max(0, producto.stock - item['cantidad'])
                producto.save(update_fields=['stock'])

            metodo_entrega = checkout_data.get('metodo_entrega', 'tienda')
            usuario = request.user if request.user.is_authenticated else None

            if metodo_entrega == 'mensajeria':
                DireccionEnvio.objects.create(
                    pedido=pedido,
                    usuario=usuario,
                    nombre_completo=checkout_data.get('nombre', ''),
                    telefono=checkout_data.get('telefono', ''),
                    direccion=checkout_data.get('direccion', ''),
                    ciudad=checkout_data.get('reparto_nombre', ''),
                    provincia=checkout_data.get('provincia_nombre', ''),
                    pais='Cuba',
                )
            else:
                tienda = Tienda.objects.filter(activa=True).first()
                DireccionEnvio.objects.create(
                    pedido=pedido,
                    usuario=usuario,
                    nombre_completo=checkout_data.get('nombre', ''),
                    telefono=checkout_data.get('telefono', ''),
                    direccion=tienda.direccion if tienda else 'Recoger en tienda',
                    ciudad='Recoger en tienda',
                    provincia='La Habana',
                    pais='Cuba',
                )

            Pago.objects.create(
                pedido=pedido,
                monto=total,
                metodo_pago='efectivo',
                estado='pendiente',
            )

            request.session.pop('carrito', None)
            request.session.pop('checkout_data', None)

            messages.success(
                request,
                f'¡Pedido creado exitosamente! Tu número de pedido es: {pedido.id_pedido}'
            )
            return redirect('checkout:confirmacion', pedido_id=pedido.id)

    except Exception as e:
        messages.error(request, f'Error al crear el pedido: {str(e)}')
        return redirect('checkout:index')


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
