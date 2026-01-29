#!/bin/bash
# Script de build para Render

echo "=== FAZENDO BUILD DA APLICAÇÃO ==="

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalações
echo "Django: $(python -c "import django; print(django.get_version())")"
echo "Psycopg2: $(python -c "import psycopg2; print(psycopg2.__version__)")"

# Tornar scripts executáveis
chmod +x startup.sh
chmod +x build.sh

echo "=== BUILD COMPLETO ==="