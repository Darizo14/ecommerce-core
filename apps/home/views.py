from django.shortcuts import render
from apps.products.models import Producto, Categoria

def home(request):
    productos_destacados = Producto.objects.filter(activo=True)[:8]                                     # Muestra los 8 productos destacados más recientes
    productos_nuevos = Producto.objects.filter(activo=True).order_by('-creado_en')[:8]                                  # Muestra los 8 productos más recientes


    return render(request, 'home/home.html', {
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
    })