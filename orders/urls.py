from django.urls import path
from .views import create_order, adams_callback

urlpatterns = [
    path('orders/', create_order),
    path('adams/callback/', adams_callback),
]
