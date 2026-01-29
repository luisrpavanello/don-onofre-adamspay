#!/usr/bin/env python
"""
Script para forçar migrações no Render.
Execute manualmente se necessário.
"""
import os
import sys
import django

# Configurar ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dononofre.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

print("=== EXECUTANDO MIGRAÇÕES FORÇADAS ===")

try:
    # Executar migrações
    execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("✓ Migrações executadas com sucesso!")
    
    # Verificar
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"✓ Tabelas no banco: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"✗ Erro: {e}")
    sys.exit(1)