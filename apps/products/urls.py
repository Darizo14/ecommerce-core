from django.urls import path
from .views import lista_productos, detalle_producto, buscar_productos

urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('buscar/', buscar_productos, name='buscar_productos'),
    path('<int:producto_id>/', detalle_producto, name='detalle_producto'),
]