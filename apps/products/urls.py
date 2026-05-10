from django.urls import path
from .views import lista_productos, detalle_producto

urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('<int:producto_id>/', detalle_producto, name='detalle_producto'),
]