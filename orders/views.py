import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

@api_view(['POST'])
def create_order(request):
    order = Order.objects.create(
        product_name=request.data['product_name'],
        amount=request.data['amount']
    )

    # Simulação AdamsPay
    order.payment_link = f"https://simulator.adamspay.com/pay/{order.id}"
    order.save()

    return Response(OrderSerializer(order).data)

@api_view(['POST'])
def adams_callback(request):
    order_id = request.data.get('external_reference')
    status = request.data.get('status')

    try:
        order = Order.objects.get(id=order_id)
        order.status = 'PAID' if status == 'paid' else 'FAILED'
        order.save()
    except Order.DoesNotExist:
        pass

    return Response({"ok": True})
