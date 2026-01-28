from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('orders/', views.create_order, name='create_order'),
    path('adams/callback/', views.adams_callback, name='adams_callback'),
]