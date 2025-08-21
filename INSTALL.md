# Guia de Instalação - Bot Telegram VIP

Este guia fornece instruções passo a passo para instalar e configurar o Bot Telegram VIP.

## 📋 Pré-requisitos

### 1. Sistema Operacional
- Linux (Ubuntu 20.04+ recomendado)
- Windows 10+ com WSL2
- macOS 10.15+

### 2. Software Necessário
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### 3. Contas e Acessos
- Conta no Telegram
- Grupo VIP criado no Telegram
- API PIX (opcional para produção)

## 🚀 Instalação Passo a Passo

### Passo 1: Criar o Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot` para criar um novo bot
3. Escolha um nome para seu bot (ex: "Meu Bot VIP")
4. Escolha um username único (ex: "meu_bot_vip_bot")
5. **Salve o token** fornecido pelo BotFather

### Passo 2: Configurar o Grupo VIP

1. Crie um grupo no Telegram ou use um existente
2. Adicione seu bot ao grupo como administrador
3. Conceda as seguintes permissões ao bot:
   - Deletar mensagens
   - Banir usuários
   - Convidar usuários
   - Gerenciar convites

### Passo 3: Obter IDs Necessários

#### ID do Grupo:
1. Adicione o bot `@userinfobot` ao seu grupo
2. O bot enviará o ID do grupo (ex: `-1001234567890`)
3. Remova o `@userinfobot` do grupo

#### Seu ID de Usuário:
1. Envie `/start` para `@userinfobot` em uma conversa privada
2. Anote seu ID de usuário (ex: `123456789`)

### Passo 4: Baixar e Instalar o Bot

```bash
# Clone o repositório (ou extraia o arquivo ZIP)
git clone <url-do-repositorio>
cd telegram_vip_bot

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo de configuração
cp .env.example .env
```

### Passo 5: Configurar Variáveis de Ambiente

Edite o arquivo `.env` com suas informações:

```env
# OBRIGATÓRIO: Token do bot
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ

# OBRIGATÓRIO: ID do grupo VIP (com o sinal de menos)
GROUP_ID=-1001234567890

# OBRIGATÓRIO: Seu ID de usuário (para comandos admin)
ADMIN_USER_ID=123456789

# OPCIONAL: Configuração da API PIX
PIX_API_URL=https://api.exemplo.com/pix
PIX_API_KEY=sua_chave_api_pix

# OPCIONAL: Preços personalizados (em centavos)
PRICE_7_DAYS=1500     # R$ 15,00
PRICE_15_DAYS=2500    # R$ 25,00
PRICE_30_DAYS=4000    # R$ 40,00
PRICE_LIFETIME=10000  # R$ 100,00
```

### Passo 6: Testar a Instalação

```bash
# Entre no diretório src
cd src

# Execute o bot
python bot.py
```

Se tudo estiver correto, você verá:
```
INFO - Bot iniciado com sucesso!
INFO - Agendador de tarefas iniciado
```

### Passo 7: Testar o Bot

1. Envie `/start` para seu bot em uma conversa privada
2. Teste os botões e navegação
3. Como admin, teste o comando `/stats`
4. Verifique se os logs estão sendo gerados em `logs/bot.log`

## 🔧 Configuração Avançada

### Executar como Serviço (Linux)

1. Crie o arquivo de serviço:
```bash
sudo nano /etc/systemd/system/telegram-vip-bot.service
```

2. Adicione o conteúdo:
```ini
[Unit]
Description=Telegram VIP Bot
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/telegram_vip_bot/src
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Ative o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-vip-bot
sudo systemctl start telegram-vip-bot
```

### Configurar Proxy (se necessário)

Se você estiver em um país onde o Telegram é bloqueado:

```bash
export HTTPS_PROXY=http://proxy:porta
export HTTP_PROXY=http://proxy:porta
```

### Configurar API PIX Real

Para integrar com uma API PIX real, você precisa:

1. Obter credenciais da sua instituição financeira
2. Implementar os métodos específicos em `pix_integration.py`
3. Configurar as variáveis `PIX_API_URL` e `PIX_API_KEY`

## 🚨 Solução de Problemas

### Erro: "Token inválido"
- Verifique se copiou o token completo do BotFather
- Certifique-se de não ter espaços extras no arquivo `.env`

### Erro: "Chat not found"
- Verifique se o GROUP_ID está correto (com sinal de menos)
- Confirme se o bot foi adicionado ao grupo
- Certifique-se de que o bot tem permissões de administrador

### Bot não remove usuários
- Verifique as permissões do bot no grupo
- Teste o comando `/checkexpired` manualmente
- Consulte os logs para erros específicos

### Dependências não instalam
```bash
# Atualize o pip
pip install --upgrade pip

# Instale dependências uma por uma
pip install python-telegram-bot
pip install requests
pip install schedule
pip install python-dotenv
pip install qrcode[pil]
```

### Erro de permissão no Linux
```bash
# Dê permissão de execução
chmod +x src/bot.py

# Ou execute com python explicitamente
python3 src/bot.py
```

## 📊 Verificação da Instalação

### Checklist de Funcionamento

- [ ] Bot responde ao comando `/start`
- [ ] Botões inline funcionam corretamente
- [ ] Comando `/stats` retorna estatísticas (admin)
- [ ] Logs são gerados em `logs/bot.log`
- [ ] Banco de dados é criado em `database/vip_bot.db`
- [ ] Sistema de agendamento está ativo

### Arquivos que Devem Existir Após a Instalação

```
telegram_vip_bot/
├── src/
│   ├── bot.py ✓
│   ├── config.py ✓
│   ├── database_manager.py ✓
│   ├── subscription_manager.py ✓
│   ├── pix_integration.py ✓
│   └── scheduler.py ✓
├── database/
│   └── vip_bot.db (criado automaticamente)
├── logs/
│   └── bot.log (criado automaticamente)
├── .env ✓
├── requirements.txt ✓
└── README.md ✓
```

## 🔄 Atualizações

Para atualizar o bot:

1. Pare o bot (Ctrl+C ou `sudo systemctl stop telegram-vip-bot`)
2. Faça backup do banco de dados
3. Baixe a nova versão
4. Execute `pip install -r requirements.txt` novamente
5. Reinicie o bot

## 📞 Suporte

Se você encontrar problemas durante a instalação:

1. Verifique os logs em `logs/bot.log`
2. Confirme todas as configurações no arquivo `.env`
3. Teste cada componente individualmente
4. Consulte a documentação do python-telegram-bot

---

**Instalação concluída com sucesso! Seu bot está pronto para gerenciar seu grupo VIP.**

