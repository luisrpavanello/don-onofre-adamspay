#!/bin/bash
# Script de inicialización para Render

echo "Iniciando aplicación Don Onofre"
echo "Directorio: $(pwd)"
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "DATABASE_URL: $DATABASE_URL"
echo "RENDER: $RENDER"
echo "PORT: $PORT"

# Activar entorno virtual (si es necesario)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Entorno virtual activado"
fi

# 1. Aplicar migraciones - ¡CRÍTICO!
echo ""
echo "Aplicando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "Migraciones aplicadas"

# 2. Verificar tablas creadas
echo ""
echo "Verificando tablas en la base de datos..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name\")
        tables = cursor.fetchall()
        print(f'✓ Total de tablas: {len(tables)}')
        for table in tables:
            print(f'  - {table[0]}')
except Exception as e:
    print(f'Error al verificar tablas: {e}')
"

# 3. Recopilar archivos estáticos
echo ""
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "Archivos estáticos recopilados"

# 4. Verificar si el directorio staticfiles existe
echo ""
echo "Verificando directorio staticfiles..."
if [ -d "staticfiles" ]; then
    echo "Directorio staticfiles existe"
    echo "Contenido: $(ls -la staticfiles/)"
else
    echo "Directorio staticfiles no existe - creando..."
    mkdir -p staticfiles
fi

# 5. Iniciar servidor
echo ""
echo "Iniciando Servidor Gunicorn..."
echo "URL: http://0.0.0.0:$PORT"
echo "========================================="
exec gunicorn dononofre.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -