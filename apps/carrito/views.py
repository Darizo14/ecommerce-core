from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.products.models import Producto


def vista_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            precio = float(producto.precio)
            subtotal = precio * cantidad
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal
            })
            total += subtotal
        except Producto.DoesNotExist:
            continue
    
    return render(request, 'carrito/carrito.html', {
        'productos': productos,
        'total': total,
    })


def agregar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        return redirect('carrito:vista_carrito')
    
    if producto.stock == 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Producto agotado'})
        return redirect('carrito:vista_carrito')
    
    cantidad = int(request.GET.get('cantidad', 1))
    cantidad = max(1, cantidad)
    
    nueva_cantidad = carrito.get(str(producto_id), 0) + cantidad
    if nueva_cantidad > producto.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': f'Solo hay {producto.stock} unidades disponibles'})
        return redirect('carrito:vista_carrito')
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)] += cantidad
    else:
        carrito[str(producto_id)] = cantidad
    
    request.session['carrito'] = carrito
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cantidad_total = sum(carrito.values())
        return JsonResponse({
            'success': True,
            'message': f'{producto.nombre} agregado al carrito',
            'cantidad_total': cantidad_total,
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'imagen': producto.imagen.url if producto.imagen else None
            }
        })
    
    return redirect('carrito:vista_carrito')


def sumar_1(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)] += 1
        request.session['carrito'] = carrito
    
    return redirect('carrito:vista_carrito')


def restar_1(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        if carrito[str(producto_id)] > 1:
            carrito[str(producto_id)] -= 1
        else:
            del carrito[str(producto_id)]
        request.session['carrito'] = carrito
    
    return redirect('carrito:vista_carrito')


def eliminar_de_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
    
    return redirect('carrito:vista_carrito')


def obtener_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            productos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria.nombre if producto.categoria else '',
                'precio': str(producto.precio),
                'cantidad': cantidad,
                'subtotal': float(producto.precio * cantidad),
                'imagen': producto.imagen.url if producto.imagen else None
            })
            total += float(producto.precio * cantidad)
        except Producto.DoesNotExist:
            continue
    
    return JsonResponse({
        'productos': productos,
        'total': total,
        'cantidad_total': sum(carrito.values())
    })