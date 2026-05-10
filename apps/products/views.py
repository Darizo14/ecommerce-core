from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria

def lista_productos(request):                               #Muestra una lista de productos disponibles en la tienda, filtrados por su estado activo. También muestra las categorías disponibles para que los usuarios puedan filtrar los productos por categoría.
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.filter(activo=True, padre__isnull=True)

    categorias_ids = request.GET.getlist('categorias')
    
    if categorias_ids:
        productos = productos.filter(categoria_id__in=categorias_ids)

    #Filtrar los productos por categoría si se ha seleccionado una categoría específica a través de la URL (por ejemplo, /productos/?categoria=1). Si no se ha seleccionado ninguna categoría, se muestran todos los productos activos. Finalmente, se renderiza la plantilla HTML con la lista de productos y categorías disponibles.
    return render(request, 'products/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categorias_seleccionadas': categorias_ids,
    })

# NUEVA VISTA
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, 'products/detalle_producto.html', {
        'producto': producto,
    })

