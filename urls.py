from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('carrito/', include('apps.carrito.urls')),  # Sin namespace aquí, usa app_name en carrito/urls.py
    path('checkout/', include('apps.checkout.urls')),
]