#!/bin/bash
# Configuração completa do ambiente Don Onofre

echo '=== CONFIGURANDO AMBIENTE DON ONOFRE ==='

# 1. Verificar se estamos na pasta correta
PROJECT_DIR="/home/luisrpavanello/LRP/don-onofre-adamspay"
if [ "$(pwd)" != "$PROJECT_DIR" ]; then
    echo "ERRO: Execute este script da pasta do projeto: $PROJECT_DIR"
    echo "Você está em: $(pwd)"
    exit 1
fi

# 2. Ativar ambiente virtual
if [ ! -d "venv_dononofre" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv_dononofre
fi

source venv_dononofre/bin/activate
echo "✓ Ambiente virtual ativado: $(which python)"

# 3. Instalar/atualizar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
export DJANGO_SETTINGS_MODULE="dononofre.settings"
export DJANGO_SECRET_KEY="dononofre-dev-secret-xyz-789"
export PYTHONPATH="/home/luisrpavanello/LRP/don-onofre-adamspay:$PYTHONPATH"

echo "✓ Variáveis configuradas:"
echo "  - DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "  - PYTHONPATH configurado"

# 5. Verificar banco de dados
if [ ! -f "db.sqlite3" ]; then
    echo "Criando banco de dados..."
    python manage.py makemigrations
    python manage.py migrate
    echo "✓ Banco de dados criado"
fi

echo ''
echo '=== AMBIENTE CONFIGURADO COM SUCESSO ==='
echo 'Comandos disponíveis:'
echo '  ./run.sh           - Iniciar servidor'
echo '  ./test_api.sh      - Testar API'
echo '  ./deploy.sh        - Fazer deploy no Render'
echo ''

chmod +x setup_env.sh