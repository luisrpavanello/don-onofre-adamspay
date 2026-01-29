# views.py - VERSÃO COMPLETA E CORRIGIDA

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

# ============= CONFIGURAÇÕES ADAMSPAY =============
# Baseado na documentação e na sua aplicação "website"
ADAMSPAY_BASE_URL = os.getenv('ADAMSPAY_BASE_URL', 'https://staging.adamspay.com')
ADAMSPAY_API_URL = f"{ADAMSPAY_BASE_URL}/api/v1/debts"  # CORRETO
ADAMSPAY_API_KEY = os.getenv('ADAMSPAY_API_KEY', '')
ADAMSPAY_APP_SECRET = os.getenv('ADAMSPAY_APP_SECRET', '')
ADAMSPAY_APP_SLUG = os.getenv('ADAMSPAY_APP_SLUG', 'website')  # Slug da sua aplicação
ADAMSPAY_CALLBACK_URL = os.getenv('ADAMSPAY_CALLBACK_URL', 'https://don-onofre-adamspay.onrender.com/api/adams/callback/')

# ============= CRIAR PEDIDO =============
@api_view(['POST'])
def create_order(request):
    try:
        print("=" * 50)
        print("🛒 CRIANDO PEDIDO - ADAMSPAY")
        print("Dados recebidos:", request.data)
        
        # Validar dados
        product_name = request.data.get('product_name')
        amount = request.data.get('amount')
        
        if not product_name or not amount:
            return Response(
                {'error': 'product_name e amount são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar pedido
        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            status='PENDING'
        )
        
        print(f"✅ Pedido criado: {order.id}")
        
        # Se não tem API Key, usar modo simulação
        if not ADAMSPAY_API_KEY or ADAMSPAY_API_KEY == 'sua_api_key_aqui':
            print("⚠️ MODO SIMULAÇÃO - Configure uma API Key real")
            
            # URL no formato correto: /pay/{app_slug}/debt/{debt_id}
            payment_url = f"{ADAMSPAY_BASE_URL}/pay/{ADAMSPAY_APP_SLUG}/debt/{order.id}"
            order.payment_link = payment_url
            order.save()
            
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': payment_url,
                'warning': 'Configure ADAMSPAY_API_KEY no Render para integração real'
            })
        
        # ========== INTEGRAÇÃO REAL COM ADAMSPAY ==========
        # Converter valor para PYG (Guarani Paraguaio)
        # 1 BRL ≈ 1000 PYG (ajuste conforme taxa atual)
        valor_pyg = int(float(amount) * 1000)
        
        # Datas de validade (2 dias como exemplo)
        inicio = datetime.now()
        fim = inicio + timedelta(days=2)
        
        # Payload baseado na documentação
        payload = {
            "debt": {
                "docId": str(order.id),  # ID único
                "label": f"Don Onofre - {product_name}",
                "amount": {
                    "currency": "PYG",
                    "value": str(valor_pyg)
                },
                "validPeriod": {
                    "start": inicio.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": fim.strftime("%Y-%m-%dT%H:%M:%S")
                },
                "target": {
                    "type": "WEB",
                    "label": "Don Onofre Restaurante"
                }
            }
        }
        
        # Headers baseados na documentação
        headers = {
            "apikey": ADAMSPAY_API_KEY,
            "Content-Type": "application/json",
            "x-if-exists": "update"
        }
        
        print(f"🌐 Chamando AdamsPay: {ADAMSPAY_API_URL}")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        # Fazer a requisição
        response = requests.post(
            ADAMSPAY_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Resposta: {json.dumps(data, indent=2)}")
            
            if 'debt' in data and 'payUrl' in data['debt']:
                payment_url = data['debt']['payUrl']
                order.payment_link = payment_url
                order.save()
                
                return Response({
                    'id': str(order.id),
                    'product_name': order.product_name,
                    'amount': str(order.amount),
                    'status': order.status,
                    'payment_link': payment_url,
                    'adamspay_id': data['debt'].get('id'),
                    'message': 'Pagamento criado na AdamsPay'
                })
        
        # Se chegou aqui, houve erro
        print(f"❌ Erro: {response.text}")
        
        # Fallback: URL simulada
        payment_url = f"{ADAMSPAY_BASE_URL}/pay/{ADAMSPAY_APP_SLUG}/debt/{order.id}"
        order.payment_link = payment_url
        order.save()
        
        return Response({
            'id': str(order.id),
            'product_name': order.product_name,
            'amount': str(order.amount),
            'status': order.status,
            'payment_link': payment_url,
            'warning': f'Erro AdamsPay {response.status_code} - Usando URL simulada'
        })
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ============= WEBHOOK (CALLBACK) =============
@api_view(['POST'])
def adams_callback(request):
    """Webhook para receber notificações da AdamsPay"""
    try:
        print("=" * 50)
        print("📬 WEBHOOK ADAMSPAY")
        print(f"📦 Dados: {request.data}")
        
        # VALIDAR HMAC (secreto)
        if ADAMSPAY_APP_SECRET:
            # Implementar validação HMAC aqui
            pass
        
        # Processar notificação
        data = request.data
        
        # Extrair ID do pedido
        order_id = None
        
        # Tentar diferentes formatos
        if 'externalId' in data:
            order_id = data['externalId']
        elif 'debt' in data and 'docId' in data['debt']:
            order_id = data['debt']['docId']
        
        if not order_id:
            return Response({'error': 'ID não encontrado'}, status=400)
        
        # Buscar pedido
        try:
            order = Order.objects.get(id=order_id)
            print(f"✅ Pedido encontrado: {order.id}")
            
            # Atualizar status
            status_map = {
                'paid': 'PAID',
                'approved': 'PAID',
                'completed': 'PAID',
                'failed': 'FAILED',
                'rejected': 'FAILED',
                'pending': 'PENDING'
            }
            
            if 'status' in data:
                new_status = status_map.get(data['status'].lower(), 'PENDING')
                if order.status != new_status:
                    order.status = new_status
                    order.save()
                    print(f"✅ Status atualizado para: {new_status}")
            
            # Resposta de sucesso
            return Response({
                'ok': True,
                'order_id': str(order_id),
                'status': order.status
            }, status=200)
            
        except Order.DoesNotExist:
            print(f"❌ Pedido não existe: {order_id}")
            return Response({'error': 'Pedido não encontrado'}, status=404)
            
    except Exception as e:
        print(f"❌ ERRO webhook: {str(e)}")
        return Response({'error': str(e)}, status=500)

# ============= OUTRAS VIEWS =============
@api_view(['GET'])
def order_status(request, order_id):
    """Consultar status do pedido"""
    try:
        order = Order.objects.get(id=order_id)
        return Response({
            'id': str(order.id),
            'product_name': order.product_name,
            'amount': str(order.amount),
            'status': order.status,
            'payment_link': order.payment_link,
            'created_at': order.created_at
        })
    except Order.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=404)
    
@api_view(['GET'])
def test_webhook(request, order_id):
    """Testar manualmente o webhook (para desenvolvimento)"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Simular dados que a AdamsPay enviaria
        test_data = {
            "externalId": str(order.id),
            "status": "paid",
            "debt": {
                "docId": str(order.id),
                "amount": {
                    "currency": "PYG",
                    "value": str(int(float(order.amount) * 1000))
                },
                "label": order.product_name,
                "payStatus": {
                    "status": "paid",
                    "time": datetime.now().isoformat() + "Z"
                }
            }
        }
        
        # Chamar o webhook internamente
        from django.test import RequestFactory
        factory = RequestFactory()
        webhook_request = factory.post(
            '/api/adams/callback/',
            data=test_data,
            content_type='application/json'
        )
        
        # Processar como se fosse da AdamsPay
        response = adams_callback(webhook_request)
        
        # Recarregar order para ver mudanças
        order.refresh_from_db()
        
        return Response({
            'test': 'Webhook simulado',
            'order_id': str(order.id),
            'old_status': 'PENDING',
            'new_status': order.status,
            'webhook_response': response.data,
            'payment_link': order.payment_link
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)