from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from apps.products.models import Producto


MAX_CANTIDAD = 99


def _obtener_carrito_limpio(request):
    carrito = request.session.get('carrito', {})
    product_ids = [pid for pid in carrito.keys() if pid.isdigit()]
    deleted = []

    if product_ids:
        existing = set(Producto.objects.filter(id__in=product_ids).values_list('id', flat=True))
        existing = {str(e) for e in existing}
        for pid in list(carrito.keys()):
            if pid.isdigit() and pid not in existing:
                deleted.append(pid)
                carrito.pop(pid, None)

    if deleted:
        request.session['carrito'] = carrito

    return carrito


def vista_carrito(request):
    carrito = _obtener_carrito_limpio(request)
    productos = []
    total = Decimal('0.00')

    if carrito:
        product_ids = [pid for pid in carrito.keys() if pid.isdigit()]
        product_map = {str(p.id): p for p in Producto.objects.filter(id__in=product_ids).select_related('categoria')}

        for producto_id, cantidad in carrito.items():
            producto = product_map.get(producto_id)
            if not producto:
                continue
            precio = producto.precio
            subtotal = precio * cantidad
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal,
            })
            total += subtotal

    return render(request, 'carrito/carrito.html', {
        'productos': productos,
        'total': total,
    })


@require_POST
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

    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        cantidad = 1
    cantidad = max(1, min(cantidad, MAX_CANTIDAD))

    nueva_cantidad = carrito.get(str(producto_id), 0) + cantidad
    if nueva_cantidad > producto.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': f'Solo hay {producto.stock} unidades disponibles'})
        return redirect('carrito:vista_carrito')

    if nueva_cantidad > MAX_CANTIDAD:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': f'Máximo {MAX_CANTIDAD} unidades por producto'})
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
                'imagen': producto.imagen.url if producto.imagen else None,
            },
        })

    return redirect('carrito:vista_carrito')


@require_POST
def sumar_1(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        try:
            producto = Producto.objects.get(id=producto_id)
            if carrito[str(producto_id)] < producto.stock:
                carrito[str(producto_id)] += 1
                request.session['carrito'] = carrito
        except Producto.DoesNotExist:
            pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cantidad_total': sum(carrito.values())})
    return redirect('carrito:vista_carrito')


@require_POST
def restar_1(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        if carrito[str(producto_id)] > 1:
            carrito[str(producto_id)] -= 1
        else:
            del carrito[str(producto_id)]
        request.session['carrito'] = carrito

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cantidad_total': sum(carrito.values())})
    return redirect('carrito:vista_carrito')


@require_POST
def eliminar_de_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cantidad_total': sum(carrito.values())})
    return redirect('carrito:vista_carrito')


def obtener_carrito(request):
    carrito = _obtener_carrito_limpio(request)
    productos = []
    total = Decimal('0.00')

    if carrito:
        product_ids = [pid for pid in carrito.keys() if pid.isdigit()]
        product_map = {
            str(p.id): p
            for p in Producto.objects.filter(id__in=product_ids).select_related('categoria')
        }

        for producto_id, cantidad in carrito.items():
            producto = product_map.get(producto_id)
            if not producto:
                continue
            subtotal = producto.precio * cantidad
            productos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria.nombre if producto.categoria else '',
                'precio': str(producto.precio),
                'cantidad': cantidad,
                'subtotal': float(subtotal),
                'imagen': producto.imagen.url if producto.imagen else None,
            })
            total += subtotal

    return JsonResponse({
        'productos': productos,
        'total': float(total),
        'cantidad_total': sum(carrito.values()),
    })
