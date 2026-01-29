#!/bin/bash
# Crear script para renderizar

echo "Construyendo la aplicación "

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Comprobar instalaciones
echo "Django: $(python -c "import django; print(django.get_version())")"
echo "Psycopg2: $(python -c "import psycopg2; print(psycopg2.__version__)")"

echo "Build Completo"