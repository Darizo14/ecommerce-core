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


def _productos_tipo(tipo, limite):
    """Productos según el tipo de sección."""
    qs = _base_productos()
    if tipo == HomeSeccion.TIPO_DESTACADOS:
        return qs.filter(destacado=True)[:limite]
    if tipo == HomeSeccion.TIPO_MAS_VENDIDOS:
        return qs.filter(total_vendido__gt=0).order_by('-total_vendido')[:limite]
    if tipo == HomeSeccion.TIPO_OFERTAS:
        return qs.filter(en_oferta=True)[:limite]
    return qs.order_by('-creado_en')[:limite]


def _secciones_home():
    """Construye el contexto de cada sección activa según su tipo."""
    secciones = []
    for seccion in HomeSeccion.objects.filter(activo=True).order_by('orden'):
        item = {
            'seccion': seccion,
            'categorias': None,
            'productos': None,
            'etiqueta': ETIQUETAS_SECCION.get(seccion.tipo, ''),
            'link_ver_todos': None,
        }

        if seccion.tipo == HomeSeccion.TIPO_CATEGORIAS:
            item['categorias'] = _categorias_destacadas(seccion.limite)
            item['link_ver_todos'] = reverse('lista_productos')
        elif seccion.tipo == HomeSeccion.TIPO_BENEFICIOS:
            pass
        else:
            item['productos'] = _productos_tipo(seccion.tipo, seccion.limite)
            item['link_ver_todos'] = reverse('lista_productos')
            if seccion.tipo == HomeSeccion.TIPO_OFERTAS:
                item['link_ver_todos'] += '?ofertas=1'

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
