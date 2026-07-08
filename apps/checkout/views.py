import urllib.parse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import Pedido, LineaPedido, DireccionEnvio, Pago, Provincia, Municipio, Reparto, Tienda
from apps.products.models import Producto

VENDEDOR_WHATSAPP = '5354492437'


def generar_mensaje_whatsapp(pedido):
    direccion = getattr(pedido, 'direccion_envio', None)
    lineas = pedido.lineas.all()

    nombre = direccion.nombre_completo if direccion else 'N/A'
    telefono = direccion.telefono if direccion else 'N/A'
    if direccion and direccion.ciudad == 'Recoger en tienda':
        direccion_texto = 'Recoger en tienda'
    else:
        direccion_texto = f"{direccion.direccion}, {direccion.ciudad}, {direccion.provincia}" if direccion else 'N/A'

    productos_str = ''
    for linea in lineas:
        productos_str += f"- {linea.producto.nombre} x{linea.cantidad}\n"

    total_cup = float(pedido.total) * 680
    mensaje = (
        f"\U0001f6d2 Nuevo pedido:\n\n"
        f"\U0001f464 Nombre: {nombre}\n"
        f"\U0001f4cd Direcci\u00f3n: {direccion_texto}\n"
        f"\U0001f4de Tel\u00e9fono: {telefono}\n\n"
        f"\U0001f4e6 Productos:\n{productos_str}\n"
        f"\U0001f4b0 Total: ${pedido.total:.2f} USD / ${total_cup:,.2f} CUP\n\n"
        "\u00bfConfirmar pedido?"
    )

    return f"https://wa.me/{VENDEDOR_WHATSAPP}?text={urllib.parse.quote(mensaje)}"


def confirmacion_pedido(request, id_pedido):
    pedido = get_object_or_404(Pedido, id_pedido=id_pedido)
    direccion = getattr(pedido, 'direccion_envio', None)
    pago = getattr(pedido, 'pago', None)

    context = {
        'pedido': pedido,
        'lineas': pedido.lineas.all(),
        'direccion': direccion,
        'pago': pago,
        'whatsapp_url': generar_mensaje_whatsapp(pedido),
    }
    return render(request, 'checkout/confirmacion_pedido.html', context)


TIEMPOS_ENTREGA = {
    'La Habana': '24 horas',
    'Artemisa': '48 horas',
    'Mayabeque': '48 horas',
    'Pinar del Río': '72 horas',
    'Matanzas': '72 horas',
    'Cienfuegos': '3-4 días',
    'Villa Clara': '3-4 días',
    'Sancti Spíritus': '4-5 días',
    'Ciego de Ávila': '4-5 días',
    'Camagüey': '5-6 días',
    'Las Tunas': '5-6 días',
    'Holguín': '6-7 días',
    'Santiago de Cuba': '6-7 días',
    'Guantánamo': '7-10 días',
}


def validar_paso_1(data):
    errores = {}
    if not data.get('nombre', '').strip():
        errores['nombre'] = 'El nombre es obligatorio'
    if not data.get('telefono', '').strip():
        errores['telefono'] = 'El teléfono es obligatorio'
    elif not data['telefono'].strip().isdigit() or len(data['telefono'].strip()) != 8:
        errores['telefono'] = 'Debe tener exactamente 8 dígitos'
    return errores


def validar_paso_2(data):
    errores = {}
    metodo = data.get('metodo_entrega', '')
    if metodo not in ('tienda', 'mensajeria'):
        errores['metodo_entrega'] = 'Selecciona un método de entrega'
    if metodo == 'mensajeria':
        if not data.get('provincia_id'):
            errores['provincia_id'] = 'Selecciona una provincia'
        if not data.get('municipio_id'):
            errores['municipio_id'] = 'Selecciona un municipio'
        if not data.get('reparto_id'):
            errores['reparto_id'] = 'Selecciona un reparto'
        if not data.get('direccion', '').strip():
            errores['direccion'] = 'La dirección es obligatoria'
    return errores


def proceso_checkout(request):
    carrito = request.session.get('carrito', {})

    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito:vista_carrito')

    product_ids = [pid for pid in carrito.keys() if pid.isdigit()]
    productos_map = {}
    if product_ids:
        for p in Producto.objects.filter(id__in=product_ids).select_related('categoria'):
            productos_map[str(p.id)] = p

    productos = []
    subtotal = Decimal('0.00')
    deleted_ids = []

    for producto_id, cantidad in list(carrito.items()):
        producto = productos_map.get(producto_id)
        if producto is None:
            deleted_ids.append(producto_id)
            continue
        precio = producto.precio
        subtotal_item = cantidad * precio
        productos.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal_item,
        })
        subtotal += subtotal_item

    if deleted_ids:
        for pid in deleted_ids:
            carrito.pop(str(pid), None)
        request.session['carrito'] = carrito

    errores = {}

    if request.method == 'POST':
        checkout_data = request.session.get('checkout_data', {})
        accion = request.POST.get('accion', '')

        if accion == 'confirmar':
            if not checkout_data:
                messages.error(request, 'Los datos del pedido no son válidos')
                return redirect('checkout:index')
            return crear_pedido_checkout(request, productos, subtotal, checkout_data)

        paso_esperado = request.session.get('checkout_paso_esperado', 1)
        try:
            paso_actual = int(request.POST.get('paso', 1))
        except (ValueError, TypeError):
            paso_actual = 1
        paso_actual = max(1, min(paso_actual, 4))

        if paso_actual > paso_esperado + 1 or paso_actual < paso_esperado - 1:
            paso_actual = paso_esperado

        paso = paso_actual

        if paso_actual == 1 and accion == 'siguiente':
            checkout_data.update(
                nombre=request.POST.get('nombre', '').strip(),
                telefono=request.POST.get('telefono', '').strip(),
            )
            errores = validar_paso_1(checkout_data)
            if not errores:
                paso = 2
                guardar_pedido_borrador(request, checkout_data, productos, subtotal)
        elif paso_actual == 2 and accion == 'siguiente':
            checkout_data['metodo_entrega'] = request.POST.get('metodo_entrega', '')
            if checkout_data['metodo_entrega'] == 'mensajeria':
                checkout_data['provincia_id'] = request.POST.get('provincia', '')
                checkout_data['municipio_id'] = request.POST.get('municipio', '')
                checkout_data['reparto_id'] = request.POST.get('reparto', '')
                checkout_data['direccion'] = request.POST.get('direccion', '').strip()

                if checkout_data['provincia_id']:
                    try:
                        provincia = Provincia.objects.get(id=checkout_data['provincia_id'])
                        checkout_data['provincia_nombre'] = provincia.nombre
                        checkout_data['precio_envio'] = str(provincia.precio_envio)
                        checkout_data['tiempo_entrega'] = TIEMPOS_ENTREGA.get(provincia.nombre, 'Consultar')
                    except Provincia.DoesNotExist:
                        checkout_data['provincia_nombre'] = ''

                if checkout_data['municipio_id']:
                    try:
                        municipio = Municipio.objects.get(id=checkout_data['municipio_id'])
                        checkout_data['municipio_nombre'] = municipio.nombre
                        base = Decimal(checkout_data.get('precio_envio', '0') or '0')
                        checkout_data['precio_envio'] = str(base + municipio.precio_adicional)
                    except Municipio.DoesNotExist:
                        checkout_data['municipio_nombre'] = ''

                if checkout_data['reparto_id']:
                    try:
                        reparto = Reparto.objects.get(id=checkout_data['reparto_id'])
                        checkout_data['reparto_nombre'] = reparto.nombre
                    except Reparto.DoesNotExist:
                        checkout_data['reparto_nombre'] = ''
            else:
                checkout_data['provincia_id'] = ''
                checkout_data['municipio_id'] = ''
                checkout_data['reparto_id'] = ''
                checkout_data['direccion'] = ''
                checkout_data['precio_envio'] = '0'
                checkout_data['tiempo_entrega'] = ''

            errores = validar_paso_2(checkout_data)
            if not errores:
                paso = 3
        elif paso_actual == 3 and accion == 'siguiente':
            checkout_data['metodo_pago'] = 'efectivo'
            paso = 4
        elif accion == 'atras':
            paso = max(1, paso_actual - 1)

        request.session['checkout_data'] = checkout_data
        request.session['checkout_paso_esperado'] = paso
    else:
        checkout_data = {}
        paso = 1
        request.session['checkout_paso_esperado'] = 1

    precio_envio_str = checkout_data.get('precio_envio', '0')
    try:
        precio_envio = Decimal(str(precio_envio_str))
    except Exception:
        precio_envio = Decimal('0')
    total = subtotal + precio_envio

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
        'errores': errores,
    }
    return render(request, 'checkout/checkout_paso_a_paso.html', context)


def guardar_pedido_borrador(request, checkout_data, productos, subtotal):
    try:
        from django.utils import timezone
        pedido, created = Pedido.objects.get_or_create(
            usuario=request.user if request.user.is_authenticated else None,
            estado='borrador',
            defaults={
                'subtotal': subtotal,
                'total': subtotal,
                'notas': f"Nombre: {checkout_data.get('nombre', '')}, Tel: {checkout_data.get('telefono', '')}",
            },
        )
        if not created:
            pedido.notas = f"Nombre: {checkout_data.get('nombre', '')}, Tel: {checkout_data.get('telefono', '')}"
            pedido.subtotal = subtotal
            pedido.total = subtotal
            pedido.save(update_fields=['notas', 'subtotal', 'total'])

            pedido.lineas.all().delete()

        for item in productos:
            LineaPedido.objects.create(
                pedido=pedido,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                subtotal=item['subtotal'],
            )

        request.session['borrador_pedido_id'] = pedido.id
    except Exception:
        pass


@require_POST
def crear_pedido_checkout(request, productos, subtotal, checkout_data):
    try:
        with transaction.atomic():
            precio_envio_str = checkout_data.get('precio_envio', '0')
            try:
                precio_envio = Decimal(str(precio_envio_str))
            except Exception:
                precio_envio = Decimal('0')
            total = subtotal + precio_envio

            pedido = Pedido.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                subtotal=subtotal,
                costo_envio=precio_envio,
                total=total,
                notas=f"Teléfono: {checkout_data.get('telefono', '')}",
            )

            product_ids = [item['producto'].id for item in productos]
            locked_products = Producto.objects.filter(id__in=product_ids).select_for_update()
            product_map = {p.id: p for p in locked_products}

            for item in productos:
                producto = product_map.get(item['producto'].id)
                if producto is None:
                    raise ValueError(f'Producto no encontrado')
                if producto.stock < item['cantidad']:
                    raise ValueError(f'Stock insuficiente para {producto.nombre}: disponible {producto.stock}, solicitado {item["cantidad"]}')
                LineaPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal'],
                )
                producto.stock -= item['cantidad']
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
            request.session.pop('checkout_paso_esperado', None)
            request.session.pop('borrador_pedido_id', None)

            messages.success(
                request,
                f'Pedido creado exitosamente. Tu número es: {pedido.id_pedido}'
            )
            return redirect('checkout:confirmacion', id_pedido=pedido.id_pedido)

    except Exception as e:
        messages.error(request, f'Error al crear el pedido: {str(e)}')
        return redirect('checkout:index')


def api_municipios(request):
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
                    'precio_adicional': str(m.precio_adicional)
                }
                for m in municipios
            ]
        }

        return JsonResponse(data)
    except Provincia.DoesNotExist:
        return JsonResponse({'municipios': []})


def api_repartos(request):
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
