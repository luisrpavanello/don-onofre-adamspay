#!/bin/bash
# Script para ejecutar el servidor Don Onofre

# Cargar configuraciones del entorno
source setup_env.sh

echo ''
echo 'Iniciando Servidor Don Onofre'
echo 'Fecha/Hora: $(date)'
echo 'Puerto: 8001'
echo 'URL: http://localhost:8001/'
echo ''

# Verificar si el puerto 8001 está en uso
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo 'ERROR: ¡El puerto 8001 ya está en uso!'
    echo 'Proceso usando el puerto:'
    lsof -Pi :8001 -sTCP:LISTEN
    echo ''
    echo 'Opciones:'
    echo '1. Matar el proceso: kill -9 $(lsof -t -i:8001)'
    echo '2. Usar otro puerto: python manage.py runserver 8002'
    exit 1
fi

echo 'Iniciando Django...'
echo 'Presione Ctrl+C para detener'
echo '----------------------------------------'
echo ''

python manage.py runserver 8001

chmod +x run.sh