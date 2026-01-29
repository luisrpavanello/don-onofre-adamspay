"""
WSGI config for dononofre project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dononofre.settings')

# FORÇAR MIGRAÇÕES ANTES DE INICIAR
if os.getenv('RENDER'):
    print("=== AMBIENTE RENDER DETECTADO ===")
    print("Forçando migrações no PostgreSQL...")
    
    try:
        # Configurar Django
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Verificar se a tabela existe
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'orders_order'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("Tabela 'orders_order' não existe. Executando migrações...")
                
                # Executar migrações
                execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
                execute_from_command_line(['manage.py', 'migrate', '--noinput'])
                
                print("Migrações executadas com sucesso!")
                
                # Verificar novamente
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'orders_order'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                if table_exists:
                    print("✓ Tabela 'orders_order' criada com sucesso!")
                else:
                    print("✗ Ainda não foi criada!")
            else:
                print("✓ Tabela 'orders_order' já existe")
                
    except Exception as e:
        print(f"Erro ao executar migrações: {e}")
        print("Continuando sem migrações...")

application = get_wsgi_application()