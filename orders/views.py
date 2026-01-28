from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
import traceback

# Página principal
def home(request):
    return render(request, 'index.html')

# Criar pedido
@api_view(['POST'])
def create_order(request):
    try:
        # Log dos dados recebidos
        print("Dados recebidos:", request.data)
        
        # Validar dados
        product_name = request.data.get('product_name')
        amount = request.data.get('amount')
        
        if not product_name or not amount:
            return Response(
                {'error': 'product_name e amount são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar o pedido
        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            status='PENDING'  # Definir status inicial
        )
        
        # Simulação AdamsPay
        order.payment_link = f"https://simulator.adamspay.com/pay/{order.id}"
        order.save()
        
        # Log do pedido criado
        print(f"Pedido criado: {order.id}")
        
        return Response(OrderSerializer(order).data)
        
    except Exception as e:
        # Log do erro completo
        print(f"ERRO em create_order: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e), 'trace': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Webhook callback
@api_view(['POST'])
def adams_callback(request):
    try:
        order_id = request.data.get('external_reference')
        status_payment = request.data.get('status')
        
        print(f"Webhook recebido: order_id={order_id}, status={status_payment}")
        
        if not order_id:
            return Response({'error': 'external_reference é obrigatório'}, status=400)
        
        order = Order.objects.get(id=order_id)
        
        if status_payment == 'paid':
            order.status = 'PAID'
        else:
            order.status = 'FAILED'
            
        order.save()
        
        return Response({'ok': True, 'order_id': str(order_id), 'status': order.status})
        
    except Order.DoesNotExist:
        print(f"Pedido não encontrado: {order_id}")
        return Response({'error': 'Order not found'}, status=404)
    except Exception as e:
        print(f"ERRO em callback: {str(e)}")
        return Response({'error': str(e)}, status=500)