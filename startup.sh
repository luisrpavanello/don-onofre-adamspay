#!/bin/bash
# Script de inicialização para Render

echo "========================================="
echo "=== INICIANDO APLICAÇÃO DON ONOFRE ==="
echo "========================================="
echo "Diretório: $(pwd)"
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "DATABASE_URL: $DATABASE_URL"
echo "RENDER: $RENDER"
echo "PORT: $PORT"

# Ativar ambiente virtual (se necessário)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Ambiente virtual ativado"
fi

# 1. Aplicar migrações - CRÍTICO!
echo ""
echo "1. APLICANDO MIGRAÇÕES..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "✓ Migrações aplicadas"

# 2. Verificar tabelas criadas
echo ""
echo "2. VERIFICANDO TABELAS NO BANCO..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name\")
        tables = cursor.fetchall()
        print(f'✓ Total de tabelas: {len(tables)}')
        for table in tables:
            print(f'  - {table[0]}')
except Exception as e:
    print(f'✗ Erro ao verificar tabelas: {e}')
"

# 3. Coletar arquivos estáticos
echo ""
echo "3. COLETANDO ARQUIVOS ESTÁTICOS..."
python manage.py collectstatic --noinput --clear
echo "✓ Arquivos estáticos coletados"

# 4. Verificar se o diretório staticfiles existe
echo ""
echo "4. VERIFICANDO DIRETÓRIOS..."
if [ -d "staticfiles" ]; then
    echo "✓ Diretório staticfiles existe"
    echo "  Conteúdo: $(ls -la staticfiles/)"
else
    echo "⚠ Diretório staticfiles não existe - criando..."
    mkdir -p staticfiles
fi

# 5. Iniciar servidor
echo ""
echo "5. INICIANDO SERVIDOR GUNICORN..."
echo "URL: http://0.0.0.0:$PORT"
echo "========================================="
exec gunicorn dononofre.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -