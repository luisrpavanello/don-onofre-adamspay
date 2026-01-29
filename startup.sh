#!/bin/bash
# Script de inicialização para Render

echo "=== INICIANDO APLICAÇÃO ==="
echo "Diretório: $(pwd)"
echo "Python: $(python --version)"
echo "DATABASE_URL: $DATABASE_URL"
echo "RENDER: $RENDER"

# Aplicar migrações SEMPRE
echo "Aplicando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "✓ Migrações aplicadas"

# Verificar se as tabelas foram criadas
echo "Verificando tabelas no banco de dados..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\")
    tables = cursor.fetchall()
    print(f'Tabelas no banco: {tables}')
"

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
echo "✓ Arquivos estáticos coletados"

# Iniciar servidor
echo "Iniciando Gunicorn..."
exec gunicorn dononofre.wsgi:application --bind 0.0.0.0:$PORT