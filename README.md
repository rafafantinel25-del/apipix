# API PIX - Gateway de Pagamentos

Esta é uma API REST para processamento de pagamentos PIX, compatível com bots do Telegram.

## Funcionalidades

- ✅ Criação de pagamentos PIX
- ✅ Verificação de status de pagamentos
- ✅ Webhook para receber notificações do gateway
- ✅ Autenticação por API Key
- ✅ Suporte a múltiplos planos (7 dias, 15 dias, 30 dias, vitalício)

## Endpoints

### 1. Criar Pagamento PIX
```
POST /api/pix/create_payment
```

**Headers:**
```
Content-Type: application/json
X-API-Key: sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn
```

**Body:**
```json
{
  "user_id": 123456,
  "plan_type": "lifetime"
}
```

**Planos disponíveis:**
- `7_days`: R$ 9,90
- `15_days`: R$ 19,90
- `30_days`: R$ 29,90
- `lifetime`: R$ 19,97

**Resposta de sucesso:**
```json
{
  "success": true,
  "payment_id": "uuid-do-pagamento",
  "pix_code": "codigo-pix-para-copiar-e-colar",
  "qr_code": "url-do-qr-code",
  "amount": 1997,
  "expires_at": "2025-08-06T19:08:43.123456"
}
```

### 2. Verificar Status do Pagamento
```
GET /api/pix/check_payment_status/{payment_id}
```

**Headers:**
```
X-API-Key: sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn
```

**Resposta:**
```json
{
  "payment_id": "uuid-do-pagamento",
  "status": "paid",
  "user_id": 123456,
  "plan_type": "lifetime",
  "amount": 1997
}
```

**Status possíveis:**
- `pending`: Aguardando pagamento
- `paid`: Pagamento confirmado
- `expired`: Pagamento expirado
- `failed`: Pagamento falhou

### 3. Webhook (Postback)
```
POST /api/pix/webhook
```

Este endpoint recebe notificações automáticas do gateway de pagamento quando o status de uma transação é atualizada.

### 4. Health Check
```
GET /health
```

Verifica se a API está funcionando.

## Configuração

### Variáveis de Ambiente (.env)

```env
# Configurações da API PIX
MASTER_PAGAMENTOS_API_URL=https://api.masterpagamentosbr.com/v1
MASTER_PAGAMENTOS_SECRET_KEY=sua_chave_secreta_do_gateway

# Configurações da aplicação
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_flask

# Configurações de autenticação da API
PIX_API_KEY=sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn

# URL base para webhooks (necessário para deploy)
BASE_URL=https://sua-api.onrender.com
```

## Como usar no Bot Telegram

No seu bot, configure as variáveis:

```python
# Configurações da API Pix
PIX_API_URL=https://sua-api.onrender.com
PIX_API_KEY=sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn
```

### Exemplo de uso:

```python
import requests

# Criar pagamento
response = requests.post(
    f"{PIX_API_URL}/api/pix/create_payment",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": PIX_API_KEY
    },
    json={
        "user_id": user_id,
        "plan_type": "lifetime"
    }
)

# Verificar status
response = requests.get(
    f"{PIX_API_URL}/api/pix/check_payment_status/{payment_id}",
    headers={"X-API-Key": PIX_API_KEY}
)
```

## Instalação e Execução

1. Clone o repositório
2. Instale as dependências:
   ```bash
   cd pix-api
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env`
4. Execute a aplicação:
   ```bash
   python src/main.py
   ```

## Deploy

A API está pronta para deploy em serviços como Render.com, Heroku, etc.

## Estrutura do Projeto

```
pix-api/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   └── payment.py
│   ├── routes/
│   │   ├── user.py
│   │   └── pix.py
│   ├── services/
│   │   └── pix_service.py
│   ├── static/
│   ├── database/
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

## Segurança

- ✅ Autenticação por API Key
- ✅ Validação de dados de entrada
- ✅ Tratamento de erros
- ✅ CORS configurado
- ✅ Logs de segurança

## Status dos Testes

- ✅ API rodando localmente
- ✅ Endpoint de health funcionando
- ✅ Autenticação funcionando
- ✅ Endpoints PIX respondendo corretamente
- ✅ Webhook funcionando
- ⚠️ Gateway real precisa de chave válida para testes completos

