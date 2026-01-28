cat > startup.sh << 'EOF'
#!/bin/bash
# Script de inicialização para Render

echo "=== INICIANDO APLICAÇÃO ==="
echo "Diretório: $(pwd)"
echo "Python: $(python --version)"

# Verificar se é primeira execução
if [ ! -f "db_initialized" ]; then
    echo "Primeira execução - aplicando migrações..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    
    # Criar arquivo de marcação
    touch db_initialized
    echo "Migrações aplicadas!"
else
    echo "Migrações já aplicadas anteriormente"
fi

# Iniciar servidor
echo "Iniciando Gunicorn..."
exec gunicorn dononofre.wsgi
EOF

chmod +x startup.sh