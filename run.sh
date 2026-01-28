#!/bin/bash
# Script para rodar o servidor Don Onofre

# Carregar configurações do ambiente
source setup_env.sh

echo ''
echo '=== INICIANDO SERVIDOR DON ONOFRE ==='
echo 'Data/Hora: $(date)'
echo 'Porta: 8001'
echo 'URL: http://localhost:8001/'
echo ''

# Verificar se a porta 8001 está em uso
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo 'ERRO: A porta 8001 já está em uso!'
    echo 'Processo usando a porta:'
    lsof -Pi :8001 -sTCP:LISTEN
    echo ''
    echo 'Opções:'
    echo '1. Mate o processo: kill -9 $(lsof -t -i:8001)'
    echo '2. Use outra porta: python manage.py runserver 8002'
    exit 1
fi

echo 'Iniciando Django...'
echo 'Pressione Ctrl+C para parar'
echo '----------------------------------------'
echo ''

python manage.py runserver 8001

