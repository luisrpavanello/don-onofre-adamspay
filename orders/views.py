# views.py - CÓDIGO CORRIGIDO

# Configurações da AdamsPay - CORRIGIDAS
# Baseado na documentação que você enviou
ADAMSPAY_BASE_URL = os.getenv('ADAMSPAY_BASE_URL', 'https://staging.adamspay.com')
ADAMSPAY_API_URL = f"{ADAMSPAY_BASE_URL}/api/v1/debts"  # CORRETO: /api/v1/debts
ADAMSPAY_API_KEY = os.getenv('ADAMSPAY_API_KEY', 'ap-416bc88cf218f388a1782efd')
ADAMSPAY_CALLBACK_URL = os.getenv('ADAMSPAY_CALLBACK_URL', 'https://don-onofre-adamspay.onrender.com/api/adams/callback/')

# Criar pedido com integração real AdamsPay - VERSÃO CORRIGIDA
@api_view(['POST'])
def create_order(request):
    try:
        print("=" * 50)
        print("CRIANDO PEDIDO - INTEGRAÇÃO ADAMSPAY CORRIGIDA")
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
        if not ADAMSPAY_API_KEY or ADAMSPAY_API_KEY == 'ap-416bc88cf218f388a1782efd':
            print("⚠️ AVISO: Usando API Key de exemplo ou vazia")
            # URL de simulação correta baseada na documentação
            fallback_url = f"https://staging.adamspay.com/pay/onofre/debt/{order.id}"
            order.payment_link = fallback_url
            order.save()
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': fallback_url,
                'warning': 'Usando modo de simulação'
            })
        
        # Preparar payload para AdamsPay - SEGUINDO A DOCUMENTAÇÃO
        # Baseado no arquivo "API_Crear deuda [AdamsPay].pdf"
        
        # Data de expiração: 2 dias como no exemplo
        inicio_validez = datetime.now()
        fin_validez = inicio_validez + timedelta(days=2)
        
        # Formato correto baseado na documentação
        payload = {
            "debt": {
                "docId": str(order.id),  # ID único da dívida
                "label": product_name,
                "amount": {
                    "currency": "PYG",  # Moeda do Paraguai (Guarani)
                    "value": str(int(float(amount) * 1000))  # Converter para PYG (1 BRL ≈ 1000 PYG)
                },
                "validPeriod": {
                    "start": inicio_validez.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": fin_validez.strftime("%Y-%m-%dT%H:%M:%S")
                }
            }
        }
        
        # Headers baseados na documentação
        headers = {
            "apikey": ADAMSPAY_API_KEY,
            "Content-Type": "application/json",
            "x-if-exists": "update"  # Permite atualizar se já existe
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
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print(f"📥 Resposta AdamsPay - Body: {json.dumps(response_data, indent=2)}")
                
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
                    print(f"❌ Resposta inesperada da AdamsPay")
                    
                    # Fallback: criar URL manual baseada na documentação
                    # Baseado no arquivo "URL de pago [AdamsPay].pdf"
                    if 'debt' in response_data and 'id' in response_data['debt']:
                        debt_id = response_data['debt']['id']
                        fallback_url = f"{ADAMSPAY_BASE_URL}/pay/onofre/debt/{debt_id}"
                        order.payment_link = fallback_url
                        order.save()
                        
                        print(f"⚠️ Fallback URL criada: {fallback_url}")
                        
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
                        # URL de simulação baseada na documentação
                        fallback_url = f"{ADAMSPAY_BASE_URL}/pay/onofre/debt/sim-{order.id}"
                        order.payment_link = fallback_url
                        order.save()
                        
                        return Response({
                            'id': str(order.id),
                            'product_name': order.product_name,
                            'amount': str(order.amount),
                            'status': order.status,
                            'payment_link': fallback_url,
                            'warning': 'Resposta da AdamsPay sem URL de pagamento'
                        })
                        
            else:
                print(f"❌ Erro AdamsPay: {response.status_code}")
                print(f"❌ Detalhes: {response.text}")
                
                # URL de fallback baseada na documentação
                fallback_url = f"{ADAMSPAY_BASE_URL}/pay/onofre/debt/error-{order.id}"
                order.payment_link = fallback_url
                order.save()
                
                return Response({
                    'id': str(order.id),
                    'product_name': order.product_name,
                    'amount': str(order.amount),
                    'status': order.status,
                    'payment_link': fallback_url,
                    'warning': f'AdamsPay retornou erro {response.status_code}',
                    'fallback': True
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição para AdamsPay: {str(e)}")
            # URL de fallback
            fallback_url = f"{ADAMSPAY_BASE_URL}/pay/onofre/debt/conn-error-{order.id}"
            order.payment_link = fallback_url
            order.save()
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': fallback_url,
                'warning': f'Erro de conexão com AdamsPay',
                'fallback': True
            })
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO em create_order: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )