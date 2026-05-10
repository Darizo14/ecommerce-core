from django.urls import path
from .views import vista_carrito, agregar_carrito, sumar_1, restar_1, eliminar_de_carrito, obtener_carrito

app_name = 'carrito'

urlpatterns = [
    path('', vista_carrito, name='vista_carrito'),
    path('agregar/<int:producto_id>/', agregar_carrito, name='agregar_carrito'),
    path('sumar/<int:producto_id>/', sumar_1, name='sumar_1'),
    path('restar/<int:producto_id>/', restar_1, name='restar_1'),
    path('eliminar/<int:producto_id>/', eliminar_de_carrito, name='eliminar_de_carrito'),
    path('api/obtener/', obtener_carrito, name='obtener_carrito'),
]