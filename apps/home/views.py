from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Count, Q
from apps.products.models import Producto, Categoria
from .models import Banner, HomeSeccion

LIMITE_PRODUCTOS = 8
LIMITE_CATEGORIAS = 8

# Etiqueta de badge según el tipo de sección de productos.
ETIQUETAS_SECCION = {
    HomeSeccion.TIPO_NUEVOS: 'nuevo',
    HomeSeccion.TIPO_MAS_VENDIDOS: 'vendido',
}


def _base_productos():
    """Queryset base con la relación a categoría precargada (evita N+1)."""
    return Producto.objects.filter(activo=True).select_related('categoria')


def _categorias_destacadas(limite=LIMITE_CATEGORIAS):
    """Categorías activas que tengan al menos un producto activo (así el enlace siempre filtra productos)."""
    return (
        Categoria.objects
        .filter(activo=True)
        .annotate(num_productos=Count('productos', filter=Q(productos__activo=True)))
        .filter(num_productos__gt=0)
        .order_by('-num_productos', 'nombre')[:limite]
    )


def _max_descuento(productos):
    """Mayor porcentaje de descuento aplicado entre los productos en oferta."""
    max_pct = 0
    for p in productos:
        if p.en_oferta and p.precio_oferta and p.precio:
            pct = int(round((1 - p.precio_oferta / p.precio) * 100))
            if pct > max_pct:
                max_pct = pct
    return max_pct


def _productos_tipo(tipo, limite):
    """Productos según el tipo de sección."""
    qs = _base_productos()
    if tipo == HomeSeccion.TIPO_DESTACADOS:
        return qs.filter(destacado=True).order_by('orden_destacado', 'id')[:limite]
    if tipo == HomeSeccion.TIPO_MAS_VENDIDOS:
        return qs.filter(total_vendido__gt=0).order_by('-total_vendido')[:limite]
    if tipo == HomeSeccion.TIPO_OFERTAS:
        return qs.filter(en_oferta=True)[:limite]
    return qs.order_by('-creado_en')[:limite]


def _secciones_home():
    """Construye el contexto de cada sección activa según su tipo y layout."""
    secciones = []
    for seccion in HomeSeccion.objects.filter(activo=True).order_by('orden'):
        item = {
            'seccion': seccion,
            'layout': seccion.layout_efectivo,
            'categorias': None,
            'productos': None,
            'etiqueta': ETIQUETAS_SECCION.get(seccion.tipo, ''),
            'link_ver_todos': None,
            'max_descuento': None,
        }

        if seccion.tipo == HomeSeccion.TIPO_CATEGORIAS:
            item['categorias'] = _categorias_destacadas(seccion.limite)
            item['link_ver_todos'] = reverse('lista_productos')
        elif seccion.tipo == HomeSeccion.TIPO_BENEFICIOS:
            pass
        elif seccion.tipo == HomeSeccion.TIPO_EDITORIAL:
            item['editoriales'] = seccion.editoriales_activas
        elif seccion.tipo == HomeSeccion.TIPO_COLECCIONES:
            item['colecciones'] = seccion.colecciones_activas
        else:
            item['productos'] = _productos_tipo(seccion.tipo, seccion.limite)
            item['link_ver_todos'] = reverse('lista_productos')
            if seccion.tipo == HomeSeccion.TIPO_OFERTAS:
                item['link_ver_todos'] += '?ofertas=1'
                item['max_descuento'] = _max_descuento(item['productos'])

        secciones.append(item)

    return secciones


def home(request):
    banners = Banner.objects.filter(activo=True).order_by('orden')
    secciones = _secciones_home()

    return render(request, 'home/home.html', {
        'banners': banners,
        'secciones': secciones,
    })


def cambiar_moneda(request, currency):
    if currency in ('USD', 'CUP'):
        request.session['currency'] = currency
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    return redirect(referer)
