from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # Checkout paso a paso (principal)
    path('', views.proceso_checkout, name='index'),
    path('api/municipios/', views.api_municipios, name='api_municipios'),
    path('api/repartos/', views.api_repartos, name='api_repartos'),
    path('confirmacion/<uuid:id_pedido>/', views.confirmacion_pedido, name='confirmacion'),
]
