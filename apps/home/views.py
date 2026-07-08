from django.shortcuts import render, redirect
from django.urls import reverse
from apps.products.models import Producto, Categoria
from .models import Banner

def home(request):
    banners = Banner.objects.filter(activo=True).order_by('orden')
    productos_destacados = Producto.objects.filter(activo=True)[:8]
    productos_nuevos = Producto.objects.filter(activo=True).order_by('-creado_en')[:8]
    productos_ofertas = Producto.objects.filter(activo=True, en_oferta=True)[:8]

    return render(request, 'home/home.html', {
        'banners': banners,
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
        'productos_ofertas': productos_ofertas,
    })


def cambiar_moneda(request, currency):
    if currency in ('USD', 'CUP'):
        request.session['currency'] = currency
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    return redirect(referer)