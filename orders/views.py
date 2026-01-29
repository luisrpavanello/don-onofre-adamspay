from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
import traceback
import requests
import os
import json
from datetime import datetime, timedelta

# Página principal
def home(request):
    return render(request, 'index.html')

# Configurações da AdamsPay
ADAMSPAY_BASE_URL = os.getenv('ADAMSPAY_BASE_URL', 'https://app.adamspay.com')
ADAMSPAY_API_URL = f"{ADAMSPAY_BASE_URL}/api/v1/debts"  # NOTE: É /debts não /payments!
ADAMSPAY_API_KEY = os.getenv('ADAMSPAY_API_KEY', '')
# Callback URL deve ser acessível publicamente
ADAMSPAY_CALLBACK_URL = os.getenv('ADAMSPAY_CALLBACK_URL', 'https://don-onofre-adamspay.onrender.com/api/adams/callback/')

# Criar pedido com integração real AdamsPay
@api_view(['POST'])
def create_order(request):
    try:
        # Log dos dados recebidos
        print("=" * 50)
        print("CRIANDO PEDIDO - INTEGRAÇÃO ADAMSPAY")
        print("Dados recebidos:", request.data)
        
        # Validar dados
        product_name = request.data.get('product_name')
        amount = request.data.get('amount')
        
        if not product_name or not amount:
            return Response(
                {'error': 'product_name e amount são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar o pedido no nosso sistema
        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            status='PENDING'
        )
        
        print(f"✅ Pedido criado localmente: {order.id}")
        
        # Verificar se temos API Key
        if not ADAMSPAY_API_KEY:
            print("⚠️ AVISO: Sem API Key da AdamsPay, usando modo simulador")
            order.payment_link = f"{ADAMSPAY_BASE_URL}/pay/debt/{order.id}"
            order.save()
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': order.payment_link,
                'warning': 'Modo simulador - Sem API Key configurada'
            })
        
        # Preparar payload para AdamsPay
        # Data de expiração: 7 dias a partir de agora
        expiration_date = (datetime.now() + timedelta(days=7)).isoformat() + "Z"
        
        payload = {
            "debt": {
                "docId": str(order.id),  # ID único da dívida
                "amount": {
                    "currency": "PYG",  # Moeda: Guarani Paraguaio
                    "value": str(float(amount))  # Valor como string
                },
                "label": product_name,
                "validPeriod": {
                    "start": datetime.now().isoformat() + "Z",
                    "end": expiration_date
                },
                "target": {
                    "type": "WEB",
                    "label": "Don Onofre - " + product_name
                }
            },
            "options": {
                "externalId": str(order.id),  # Nosso ID de referência
                "notificationUrl": ADAMSPAY_CALLBACK_URL,
                "returnUrl": f"https://don-onofre-adamspay.onrender.com/?order_id={order.id}&status=completed",
                "cancelUrl": f"https://don-onofre-adamspay.onrender.com/?order_id={order.id}&status=cancelled"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {ADAMSPAY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"🌐 Chamando AdamsPay API: {ADAMSPAY_API_URL}")
        print(f"🔑 API Key: {ADAMSPAY_API_KEY[:10]}...")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Chamar API da AdamsPay
            response = requests.post(
                ADAMSPAY_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"📥 Resposta AdamsPay - Status: {response.status_code}")
            print(f"📥 Resposta AdamsPay - Body: {response.text}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # Verificar se a resposta tem o formato esperado
                if 'debt' in response_data and 'payUrl' in response_data['debt']:
                    payment_url = response_data['debt']['payUrl']
                    order.payment_link = payment_url
                    order.save()
                    
                    print(f"✅ Link de pagamento gerado: {payment_url}")
                    
                    return Response({
                        'id': str(order.id),
                        'product_name': order.product_name,
                        'amount': str(order.amount),
                        'status': order.status,
                        'payment_link': payment_url,
                        'adamspay_id': response_data['debt'].get('id'),
                        'message': 'Pagamento criado com sucesso na AdamsPay'
                    })
                else:
                    print(f"❌ Resposta inesperada da AdamsPay: {response_data}")
                    # Fallback: criar URL manual baseada na documentação
                    if 'debt' in response_data and 'id' in response_data['debt']:
                        debt_id = response_data['debt']['id']
                        fallback_url = f"{ADAMSPAY_BASE_URL}/pay/debt/{debt_id}"
                        order.payment_link = fallback_url
                        order.save()
                        
                        return Response({
                            'id': str(order.id),
                            'product_name': order.product_name,
                            'amount': str(order.amount),
                            'status': order.status,
                            'payment_link': fallback_url,
                            'warning': 'Estrutura de resposta inesperada, usando fallback',
                            'adamspay_response': response_data
                        })
                    else:
                        raise Exception("Resposta da AdamsPay sem URL de pagamento")
                        
            else:
                print(f"❌ Erro AdamsPay: {response.status_code}")
                print(f"❌ Detalhes: {response.text}")
                
                # Tentar parsear erro
                error_msg = "Erro ao criar pagamento"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    error_msg = response.text[:100]
                
                # Fallback: URL simulada
                fallback_url = f"{ADAMSPAY_BASE_URL}/pay/debt/simulated-{order.id}"
                order.payment_link = fallback_url
                order.save()
                
                return Response({
                    'id': str(order.id),
                    'product_name': order.product_name,
                    'amount': str(order.amount),
                    'status': order.status,
                    'payment_link': fallback_url,
                    'warning': f'AdamsPay retornou erro {response.status_code}: {error_msg}',
                    'fallback': True
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição para AdamsPay: {str(e)}")
            # Fallback para URL simulada
            fallback_url = f"{ADAMSPAY_BASE_URL}/pay/debt/error-{order.id}"
            order.payment_link = fallback_url
            order.save()
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': fallback_url,
                'warning': f'Erro de conexão com AdamsPay: {str(e)}',
                'fallback': True
            })
        
    except Exception as e:
        # Log do erro completo
        print(f"❌ ERRO CRÍTICO em create_order: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e), 'trace': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Webhook callback da AdamsPay
@api_view(['POST'])
def adams_callback(request):
    try:
        print("=" * 50)
        print("📬 WEBHOOK RECEBIDO DA ADAMSPAY")
        print(f"📋 Headers: {dict(request.headers)}")
        print(f"📦 Body (raw): {request.body}")
        print(f"📦 Body (parsed): {request.data}")
        
        # A AdamsPay envia os dados no corpo da requisição
        data = request.data
        
        # Log completo para debug
        print(f"🔍 Dados recebidos: {json.dumps(data, indent=2)}")
        
        # Extrair informações baseado na documentação da AdamsPay
        order_id = None
        status_payment = None
        debt_id = None
        
        # Tentar diferentes formatos baseado na documentação
        if 'externalId' in data:
            order_id = data['externalId']
        elif 'external_reference' in data:
            order_id = data['external_reference']
        elif 'debt' in data and 'externalId' in data['debt']:
            order_id = data['debt']['externalId']
        
        if 'status' in data:
            status_payment = data['status']
        elif 'payment' in data and 'status' in data['payment']:
            status_payment = data['payment']['status']
        
        if 'debt' in data and 'id' in data['debt']:
            debt_id = data['debt']['id']
        
        print(f"🔍 order_id={order_id}, status={status_payment}, debt_id={debt_id}")
        
        if not order_id:
            print("❌ Nenhum order_id encontrado no webhook")
            return Response({'error': 'externalId/external_reference é obrigatório'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(id=order_id)
            print(f"✅ Pedido encontrado: {order.id}")
            print(f"📊 Status atual: {order.status}")
            
            # Mapear status da AdamsPay para nosso sistema
            status_map = {
                'paid': 'PAID',
                'completed': 'PAID',
                'approved': 'PAID',
                'confirmed': 'PAID',
                'failed': 'FAILED',
                'rejected': 'FAILED',
                'expired': 'FAILED',
                'cancelled': 'FAILED',
                'pending': 'PENDING',
                'in_process': 'PENDING',
                'created': 'PENDING'
            }
            
            if status_payment:
                status_lower = status_payment.lower()
                if status_lower in status_map:
                    new_status = status_map[status_lower]
                    if order.status != new_status:
                        order.status = new_status
                        order.save()
                        print(f"✅ Status atualizado para: {new_status}")
                    else:
                        print(f"ℹ️ Status já é {new_status}, não atualizado")
                else:
                    print(f"⚠️ Status não mapeado: {status_payment}")
            else:
                print("⚠️ Nenhum status recebido no webhook")
            
            # Retornar resposta de sucesso
            response_data = {
                'ok': True,
                'order_id': str(order_id),
                'debt_id': debt_id,
                'status': order.status,
                'received_status': status_payment,
                'message': 'Webhook processado com sucesso'
            }
            
            print(f"✅ Resposta do webhook: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            print(f"❌ Pedido não encontrado: {order_id}")
            return Response({
                'error': f'Order not found: {order_id}',
                'received_data': data
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        print(f"❌ ERRO em callback: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Status do pedido (para o frontend verificar)
@api_view(['GET'])
def order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return Response({
            'id': str(order.id),
            'product_name': order.product_name,
            'amount': str(order.amount),
            'status': order.status,
            'payment_link': order.payment_link,
            'created_at': order.created_at,
            'status_display': order.get_status_display() if hasattr(order, 'get_status_display') else order.status
        })
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# Página de simulação para testes (quando não há API Key)
@api_view(['GET'])
def simulate_payment(request, order_id):
    """Página de simulação para testes"""
    try:
        order = Order.objects.get(id=order_id)
        
        context = {
            'order': order,
            'order_id': order_id,
            'product_name': order.product_name,
            'amount': order.amount,
            'status': order.status,
            'simulated': True
        }
        
        return render(request, 'simulate_payment.html', context)
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)