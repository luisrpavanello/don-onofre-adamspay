#!/bin/bash
# Configuración completa del entorno Don Onofre

echo 'Configuración completa del entorno Don Onofre'

# 1. Verificar si estamos en la carpeta correcta
PROJECT_DIR="/home/luisrpavanello/LRP/don-onofre-adamspay"
if [ "$(pwd)" != "$PROJECT_DIR" ]; then
    echo "ERROR: Ejecute este script desde la carpeta del proyecto: $PROJECT_DIR"
    echo "Usted está en: $(pwd)"
    exit 1
fi

# 2. Activar entorno virtual
if [ ! -d "venv_dononofre" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv_dononofre
fi

source venv_dononofre/bin/activate
echo "✓ Entorno virtual activado: $(which python)"

# 3. Instalar/actualizar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="dononofre.settings"
export DJANGO_SECRET_KEY="dononofre-dev-secret-xyz-789"
export PYTHONPATH="/home/luisrpavanello/LRP/don-onofre-adamspay:$PYTHONPATH"

echo "✓ Variables configuradas:"
echo "  - DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "  - PYTHONPATH configurado"

# 5. Verificar base de datos
if [ ! -f "db.sqlite3" ]; then
    echo "Creando base de datos..."
    python manage.py makemigrations
    python manage.py migrate
    echo "Base de datos creada"
fi

echo ''
echo '=== ENTORNO CONFIGURADO EXITOSAMENTE ==='
echo 'Comandos disponibles:'
echo '  ./run.sh           - Iniciar servidor'
echo '  ./test_api.sh      - Probar API'
echo '  ./deploy.sh        - Hacer deploy en Render'
echo ''

chmod +x setup_env.sh