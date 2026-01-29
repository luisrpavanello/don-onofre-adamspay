#!/usr/bin/env python
"""
Script para forzar migraciones en Render.
Ejecutar manualmente si es necesario.
"""
import os
import sys
import django

# Configurar entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dononofre.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

print("Ejecutando migraciones")

try:
    # Ejecutar migraciones
    execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("Migraciones ejecutadas exitosamente!")
    
    # Verificar
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"Tablas en la base de datos: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)