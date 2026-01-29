#!/bin/bash
# Script de inicialização para Render

echo "=== INICIANDO APLICAÇÃO ==="
echo "Diretório: $(pwd)"
echo "Python: $(python --version)"
echo "Banco de dados: $DATABASE_URL"

# Aplicar migrações sempre (importante para PostgreSQL)
echo "Aplicando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "Migrações aplicadas!"

# Iniciar servidor
echo "Iniciando Gunicorn..."
exec gunicorn dononofre.wsgi:application --bind 0.0.0.0:10000