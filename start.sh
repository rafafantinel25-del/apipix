#!/bin/bash

# Script de inicialização do Bot Telegram VIP
# Autor: Sistema de Automação
# Data: $(date +%Y-%m-%d)

echo "🤖 Iniciando Bot Telegram VIP..."
echo "=================================="

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado."
    echo "📝 Copie .env.example para .env e configure suas variáveis:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Verifica se as dependências estão instaladas
echo "📦 Verificando dependências..."
pip3 install -r requirements.txt --quiet

# Cria diretórios necessários
mkdir -p database logs

# Verifica se o arquivo de configuração tem as variáveis obrigatórias
echo "⚙️  Verificando configuração..."

if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "TELEGRAM_BOT_TOKEN=seu_token_aqui" .env; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado no arquivo .env"
    echo "   Obtenha seu token com @BotFather no Telegram"
    exit 1
fi

if ! grep -q "GROUP_ID=" .env || grep -q "GROUP_ID=-1001234567890" .env; then
    echo "❌ GROUP_ID não configurado no arquivo .env"
    echo "   Configure o ID do seu grupo VIP"
    exit 1
fi

if ! grep -q "ADMIN_USER_ID=" .env || grep -q "ADMIN_USER_ID=123456789" .env; then
    echo "❌ ADMIN_USER_ID não configurado no arquivo .env"
    echo "   Configure seu ID de usuário para comandos administrativos"
    exit 1
fi

echo "✅ Configuração verificada com sucesso!"
echo ""
echo "🚀 Iniciando o bot..."
echo "   Para parar o bot, pressione Ctrl+C"
echo "   Logs serão salvos em logs/bot.log"
echo ""

# Muda para o diretório src e executa o bot
cd src

# Executa o bot com tratamento de erro
python3 bot.py

# Se chegou aqui, o bot foi interrompido
echo ""
echo "🛑 Bot finalizado."
echo "📊 Verifique os logs em logs/bot.log para mais informações."

