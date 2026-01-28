#!/bin/bash
# Testar a API do Don Onofre

source setup_env.sh

echo ''
echo '=== TESTANDO API DON ONOFRE ==='
echo ''

echo '1. Testando página inicial...'
curl -s -o /dev/null -w "Código: %{http_code}\n" http://localhost:8001/

echo ''
echo '2. Testando criação de pedido...'
curl -X POST http://localhost:8001/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Pizza Teste", "amount": 50}' \
  -w "\nCódigo: %{http_code}\n" \
  --silent | python -m json.tool || echo "Erro no JSON"

echo ''
echo '3. Verificando banco de dados...'
python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dononofre.settings')
django.setup()
from orders.models import Order
count = Order.objects.count()
print(f'Total de pedidos no banco: {count}')
for order in Order.objects.all()[:3]:
    print(f'  - {order.product_name}: R${order.amount} ({order.status})')
PYEOF

echo ''
echo '=== TESTES CONCLUÍDOS ==='

chmod +x test_api.sh