from django.urls import path
from .views import home, cambiar_moneda

urlpatterns = [                                  
    path('', home, name='home'),
    path('moneda/<str:currency>/', cambiar_moneda, name='cambiar_moneda'),
]