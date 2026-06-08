from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Producto, Categoria

def lista_productos(request):
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.filter(activo=True, padre__isnull=True)

    categorias_ids = request.GET.getlist('categorias')
    if categorias_ids:
        productos = productos.filter(categoria_id__in=categorias_ids)

    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    solo_ofertas = request.GET.get('ofertas', '')
    if solo_ofertas:
        productos = productos.filter(en_oferta=True)

    orden = request.GET.get('orden', '')
    if orden == 'price-asc':
        productos = productos.order_by('precio')
    elif orden == 'price-desc':
        productos = productos.order_by('-precio')
    elif orden == 'name-asc':
        productos = productos.order_by('nombre')
    elif orden == 'name-desc':
        productos = productos.order_by('-nombre')
    else:
        productos = productos.order_by('-creado_en')

    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 12)
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)

    context = {
        'productos': productos_page,
        'categorias': categorias,
        'categorias_seleccionadas': categorias_ids,
        'paginator': paginator,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'solo_ofertas': solo_ofertas,
        'orden_actual': orden,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'products/lista_productos_content.html'
    else:
        template = 'products/lista_productos.html'

    return render(request, template, context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    relacionados = Producto.objects.filter(
        activo=True,
        categoria=producto.categoria
    ).exclude(id=producto.id)[:4]
    return render(request, 'products/detalle_producto.html', {
        'producto': producto,
        'relacionados': relacionados,
    })


def buscar_productos(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    productos = Producto.objects.filter(
        activo=True, nombre__icontains=q
    ).values('id', 'nombre', 'slug', 'precio')[:10]

    results = [{
        'id': p['id'],
        'nombre': p['nombre'],
        'precio': str(p['precio']),
        'url': f'/productos/{p["id"]}/',
    } for p in productos]

    return JsonResponse({'results': results})

