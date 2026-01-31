# views.py - VERSIÓN LIMPIA Y PROFESIONAL

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from .serializers import OrderSerializer
import traceback
import requests
import os
import json
import uuid
from datetime import datetime, timedelta

# Configuraciones de AdamsPay
ADAMSPAY_BASE_URL = os.getenv('ADAMSPAY_BASE_URL', 'https://staging.adamspay.com')
ADAMSPAY_API_URL = f"{ADAMSPAY_BASE_URL}/api/v1/debts"
ADAMSPAY_API_KEY = os.getenv('ADAMSPAY_API_KEY', '')
ADAMSPAY_APP_SECRET = os.getenv('ADAMSPAY_APP_SECRET', '')
ADAMSPAY_APP_SLUG = os.getenv('ADAMSPAY_APP_SLUG', 'website')
ADAMSPAY_CALLBACK_URL = os.getenv('ADAMSPAY_CALLBACK_URL', 'https://don-onofre-adamspay.onrender.com/api/adams/callback/')


def home(request):
    """
    Vista para la página principal.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la plantilla index.html.
    """
    return render(request, 'index.html')


@api_view(['POST'])
def create_order(request):
    """
    Crea un nuevo pedido y lo registra en AdamsPay.
    
    Esta vista maneja la creación de un pedido en el sistema local
    y su posterior registro en la pasarela de pagos AdamsPay.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos JSON.
            Debe contener:
            - product_name (str): Nombre del producto.
            - amount (float): Monto total en guaraníes.
    
    Returns:
        Response: JSON con los datos del pedido creado.
            - id (str): ID único del pedido.
            - product_name (str): Nombre del producto.
            - amount (str): Monto formateado.
            - status (str): Estado inicial (PENDING).
            - payment_link (str): URL para proceder al pago.
            - warning (str, opcional): Advertencias si hay problemas con AdamsPay.
    
    Raises:
        400 Bad Request: Si faltan parámetros obligatorios.
        500 Internal Server Error: Si ocurre un error inesperado.
    """
    try:
        print("Iniciando creación de pedido")
        print(f"Datos recibidos: {request.data}")
        
        # Validar datos
        product_name = request.data.get('product_name')
        amount = request.data.get('amount')
        
        if not product_name or not amount:
            return Response(
                {'error': 'product_name y amount son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear pedido en la base de datos
        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            status='PENDING'
        )
        
        print(f"Pedido creado: {order.id}")
        print(f"Valor original: {amount} (este es el valor en guaranis)")
        
        # Si no hay API Key, usar modo simulación
        if not ADAMSPAY_API_KEY or ADAMSPAY_API_KEY == 'su_api_key_aqui':
            print("Modo simulación - Configure una API Key real")
            
            payment_url = f"{ADAMSPAY_BASE_URL}/pay/{ADAMSPAY_APP_SLUG}/debt/{order.id}"
            order.payment_link = payment_url
            order.save()
            
            return Response({
                'id': str(order.id),
                'product_name': order.product_name,
                'amount': str(order.amount),
                'status': order.status,
                'payment_link': payment_url,
                'warning': 'Configure ADAMSPAY_API_KEY en Render para integración real'
            })
        
        valor_pyg = int(float(amount))
        inicio = datetime.now()
        fin = inicio + timedelta(days=2)
        
        payload = {
            "debt": {
                "docId": str(order.id),
                "label": f"Don Onofre - {product_name}",
                "amount": {
                    "currency": "PYG",
                    "value": str(valor_pyg)
                },
                "validPeriod": {
                    "start": inicio.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": fin.strftime("%Y-%m-%dT%H:%M:%S")
                },
                "target": {
                    "type": "WEB",
                    "label": "Don Onofre Restaurante"
                }
            }
        }
        
        headers = {
            "apikey": ADAMSPAY_API_KEY,
            "Content-Type": "application/json",
            "x-if-exists": "update"
        }
        
        print(f"Llamando a AdamsPay: {ADAMSPAY_API_URL}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            ADAMSPAY_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Estado de respuesta: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Respuesta AdamsPay: {json.dumps(data, indent=2)}")
            
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
                    'message': 'Pago creado en AdamsPay'
                })
        
        # Fallback si hay error
        print(f"Error en AdamsPay: {response.text}")
        
        payment_url = f"{ADAMSPAY_BASE_URL}/pay/{ADAMSPAY_APP_SLUG}/debt/{order.id}"
        order.payment_link = payment_url
        order.save()
        
        return Response({
            'id': str(order.id),
            'product_name': order.product_name,
            'amount': str(order.amount),
            'status': order.status,
            'payment_link': payment_url,
            'warning': f'Error AdamsPay {response.status_code} - Usando URL simulada'
        })
        
    except Exception as e:
        print(f"Error al crear pedido: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def order_status(request, order_id):
    """
    Consulta el estado actual de un pedido existente.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        order_id (UUID): ID único del pedido a consultar.
    
    Returns:
        Response: JSON con los datos actualizados del pedido.
            - id (str): ID del pedido.
            - product_name (str): Nombre del producto.
            - amount (str): Monto total.
            - status (str): Estado actual (PENDING/PAID/FAILED).
            - payment_link (str): URL de pago (si existe).
            - created_at (datetime): Fecha de creación.
    
    Raises:
        404 Not Found: Si el pedido no existe.
    """
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
        return Response({'error': 'Pedido no encontrado'}, status=404)


@api_view(['POST'])
def adams_callback(request):
    """
    Webhook para recibir notificaciones de AdamsPay (POST).
    
    Este endpoint recibe notificaciones asincrónicas de AdamsPay
    cuando cambia el estado de un pago.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos JSON
            de notificación de AdamsPay.
    
    Returns:
        Response: Resultado del procesamiento de la notificación.
            - ok (bool): True si se procesó correctamente.
            - order_id (str): ID del pedido actualizado.
            - status (str): Nuevo estado del pedido.
            - message (str): Mensaje descriptivo.
    
    Raises:
        500 Internal Server Error: Si ocurre un error al procesar.
    """
    try:
        print("Webhook AdamsPay recibido")
        print(f"Datos: {request.data}")
        
        # Validar HMAC si hay secreto
        if ADAMSPAY_APP_SECRET:
            pass  # Implementar validación HMAC aquí
        
        return procesar_notificacion_adams(request.data)
            
    except Exception as e:
        print(f"Error en webhook: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@csrf_exempt
def adams_redirect(request):
    """
    URL de retorno después del pago en AdamsPay (GET).
    
    Esta vista maneja la redirección del usuario después de completar
    el pago en AdamsPay. Procesa los parámetros de la URL y actualiza
    el estado del pedido.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con parámetros GET.
            Parámetros esperados:
            - order_id o externalId: ID del pedido.
            - status: Estado del pago (completed, failed, pending).
    
    Returns:
        HttpResponse: Renderiza la plantilla payment_result.html con
            los datos del pedido actualizado.
    
    Raises:
        400 Bad Request: Si no se proporciona el ID del pedido.
    """
    try:
        print("Redirect AdamsPay recibido")
        print(f"Parámetros: {dict(request.GET)}")
        
        order_id = request.GET.get('order_id') or request.GET.get('externalId')
        status_param = request.GET.get('status', '').lower()
        
        if not order_id:
            return Response({'error': 'ID no proporcionado'}, status=400)
        
        # Mapear estados de la query string
        mapa_estados = {
            'completed': 'paid',
            'paid': 'paid',
            'approved': 'paid',
            'failed': 'failed',
            'rejected': 'failed',
            'pending': 'pending'
        }
        
        datos_notificacion = {
            'externalId': order_id,
            'status': mapa_estados.get(status_param, 'pending')
        }
        
        # Procesar notificación
        resultado = procesar_notificacion_adams(datos_notificacion)
        
        # Redirigir a página de resultado
        try:
            order = Order.objects.get(id=order_id)
            return render(request, 'payment_result.html', {
                'order': order,
                'status': order.status
            })
        except Order.DoesNotExist:
            return render(request, 'payment_result.html', {
                'error': f'Pedido {order_id} no encontrado'
            })
            
    except Exception as e:
        print(f"Error en redirect: {str(e)}")
        return render(request, 'payment_result.html', {
            'error': str(e)
        })


def procesar_notificacion_adams(datos):
    """
    Procesa notificaciones de AdamsPay y actualiza el estado del pedido.
    
    Función auxiliar que extrae y procesa los datos de notificación
    de AdamsPay para actualizar el estado del pedido correspondiente.
    
    Args:
        datos (dict|str): Datos de notificación en formato JSON o dict.
            Puede contener:
            - externalId, debt.docId, id, order_id: ID del pedido.
            - status: Estado del pago.
            - debt.payStatus.status: Estado del pago en estructura anidada.
    
    Returns:
        Response: JSON con resultado del procesamiento.
            - ok (bool): True si se procesó correctamente.
            - order_id (str): ID del pedido procesado.
            - status (str): Nuevo estado del pedido.
            - previous_status (str): Estado anterior (siempre PENDING).
            - message (str): Mensaje descriptivo.
    
    Raises:
        400 Bad Request: Si no se puede extraer el ID del pedido.
        404 Not Found: Si el pedido no existe en la base de datos.
        500 Internal Server Error: Si ocurre un error inesperado.
    """
    try:
        print("Procesando notificación AdamsPay")
        print(f"Datos recibidos: {datos}")
        
        # Para debugging
        import json
        print(f"Datos como JSON: {json.dumps(datos) if isinstance(datos, dict) else datos}")
        
        # Extraer ID del pedido
        order_id = None
        
        if isinstance(datos, dict):
            if 'externalId' in datos:
                order_id = datos['externalId']
            elif 'debt' in datos and 'docId' in datos['debt']:
                order_id = datos['debt']['docId']
            elif 'id' in datos:
                order_id = datos['id']
            elif 'order_id' in datos:
                order_id = datos['order_id']
        elif isinstance(datos, str):
            try:
                datos_parseados = json.loads(datos)
                if 'externalId' in datos_parseados:
                    order_id = datos_parseados['externalId']
                elif 'debt' in datos_parseados and 'docId' in datos_parseados['debt']:
                    order_id = datos_parseados['debt']['docId']
            except:
                pass
        
        print(f"ID extraído: {order_id}")
        
        if not order_id:
            print("ID no encontrado en los datos")
            return Response({'error': 'ID no encontrado'}, status=400)
        
        try:
            # Limpiar y validar UUID
            try:
                order_uuid = uuid.UUID(str(order_id))
            except ValueError:
                print(f"ID no es un UUID válido: {order_id}")
                return Response({'error': 'UUID inválido'}, status=400)
            
            order = Order.objects.get(id=order_uuid)
            print(f"Pedido encontrado: {order.id}")
            print(f"Estado actual del pedido: {order.status}")
            
            # Determinar nuevo estado
            nuevo_estado = 'PENDING'
            
            # Mapeo de estados
            if isinstance(datos, dict):
                estado_datos = str(datos.get('status', '')).lower()
                
                # Verificar en diferentes ubicaciones posibles
                if estado_datos in ['paid', 'approved', 'completed', 'confirmed']:
                    nuevo_estado = 'PAID'
                elif estado_datos in ['failed', 'rejected', 'expired', 'cancelled']:
                    nuevo_estado = 'FAILED'
                elif estado_datos == 'pending':
                    nuevo_estado = 'PENDING'
                
                # También verificar en debt.payStatus.status
                if 'debt' in datos and 'payStatus' in datos['debt']:
                    pay_status = datos['debt']['payStatus'].get('status', '').lower()
                    if pay_status in ['paid', 'approved']:
                        nuevo_estado = 'PAID'
                    elif pay_status in ['failed', 'rejected']:
                        nuevo_estado = 'FAILED'
            
            print(f"Nuevo estado a asignar: {nuevo_estado}")
            
            # Actualizar si cambió
            if order.status != nuevo_estado:
                order.status = nuevo_estado
                order.save()
                print(f"Estado actualizado a: {nuevo_estado}")
                
                # Log para auditoría
                print(f"Auditoría - Pedido {order.id}: {order.status} -> {nuevo_estado}")
            else:
                print(f"ℹEstado ya era: {nuevo_estado}")
            
            return Response({
                'ok': True,
                'order_id': str(order_id),
                'status': order.status,
                'previous_status': 'PENDING',  # Para comparación
                'message': f'Estado actualizado a {order.status}'
            }, status=200)
            
        except Order.DoesNotExist:
            print(f"Pedido no existe en BD: {order_id}")
            
            # Listar todos los pedidos para debugging
            all_orders = Order.objects.all()
            print(f"Pedidos en BD: {[str(o.id) for o in all_orders]}")
            
            return Response({'error': 'Pedido no encontrado'}, status=404)
            
    except Exception as e:
        print(f"Error procesando notificación: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return Response({'error': str(e)}, status=500)


def payment_result(request):
    """
    Página para mostrar el resultado del proceso de pago.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
            Parámetro GET opcional:
            - order_id: ID del pedido a mostrar.
    
    Returns:
        HttpResponse: Renderiza payment_result.html con:
            - order (Order): Objeto del pedido (si existe).
            - error (str): Mensaje de error (si el pedido no existe).
    """
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            return render(request, 'payment_result.html', {'order': order})
        except Order.DoesNotExist:
            pass
    return render(request, 'payment_result.html', {'error': 'No se encontró el pedido'})


@api_view(['GET'])
def test_webhook(request, order_id):
    """
    Endpoint de prueba para simular webhooks de AdamsPay.
    
    Útil para desarrollo y testing para simular notificaciones
    de AdamsPay sin necesidad de realizar pagos reales.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        order_id (UUID): ID del pedido a testear.
    
    Returns:
        Response: JSON con resultado de la simulación.
            - test (str): Identificador de la prueba.
            - order_id (str): ID del pedido.
            - estado_anterior (str): Estado antes de la simulación.
            - estado_nuevo (str): Estado después de la simulación.
            - respuesta_webhook (dict): Respuesta del procesador.
            - payment_link (str): URL de pago asociada.
    
    Raises:
        404 Not Found: Si el pedido no existe.
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Datos de prueba simulando AdamsPay
        datos_prueba = {
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
        
        # Procesar como notificación
        response = procesar_notificacion_adams(datos_prueba)
        
        # Recargar pedido para ver cambios
        order.refresh_from_db()
        
        return Response({
            'test': 'Webhook simulado',
            'order_id': str(order.id),
            'estado_anterior': 'PENDING',
            'estado_nuevo': order.status,
            'respuesta_webhook': response.data,
            'payment_link': order.payment_link
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Pedido no encontrado'}, status=404)