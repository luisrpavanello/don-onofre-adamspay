"""
Configuración WSGI para el proyecto dononofre.

Expone la aplicación WSGI como una variable a nivel de módulo llamada ``application``.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dononofre.settings')

# Migraciones antes de iniciar
if os.getenv('RENDER'):
    print("Entorno render detectado")
    print("Migraciones en PostgreSQL...")
    
    try:
        # Configurar Django
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Verificar si la tabla existe
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
                print("Tabla 'orders_order' no existe. Ejecutando migraciones...")
                
                # Ejecutar migraciones
                execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
                execute_from_command_line(['manage.py', 'migrate', '--noinput'])
                
                print("Migraciones ejecutadas con éxito!")
                
                # Verificar nuevamente
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'orders_order'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                if table_exists:
                    print("Tabla 'orders_order' creada con éxito!")
                else:
                    print("¡Aún no se ha creado!")
            else:
                print("Tabla 'orders_order' ya existe")
                
    except Exception as e:
        print(f"Error al ejecutar migraciones: {e}")
        print("Continuando sin migraciones...")

application = get_wsgi_application()