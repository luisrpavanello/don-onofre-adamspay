from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.home, name='home'),
    path('orders/', views.create_order, name='create_order'),
    path('orders/<uuid:order_id>/', views.order_status, name='order_status'),
    path('adams/callback/', views.adams_callback, name='adams_callback'),
    path('adams/redirect/', views.adams_redirect, name='adams_redirect'),
    path('payment-result/', views.payment_result, name='payment_result'),
    path('test-webhook/<uuid:order_id>/', views.test_webhook, name='test_webhook'),
]