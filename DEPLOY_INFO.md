# Informações do Deploy - API PIX

## URL da API Deployada
```
https://p9hwiqcnqlp5.manus.space
```

## Endpoints Disponíveis

### Health Check
```
GET https://p9hwiqcnqlp5.manus.space/health
```

### Criar Pagamento PIX
```
POST https://p9hwiqcnqlp5.manus.space/api/pix/create_payment
```

### Verificar Status do Pagamento
```
GET https://p9hwiqcnqlp5.manus.space/api/pix/check_payment_status/{payment_id}
```

### Webhook
```
POST https://p9hwiqcnqlp5.manus.space/api/pix/webhook
```

## Configuração para o Bot Telegram

No seu bot, use estas configurações:

```python
# Configurações da API Pix
PIX_API_URL=https://p9hwiqcnqlp5.manus.space
PIX_API_KEY=sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn
```

## Status do Deploy
- ✅ API deployada com sucesso
- ✅ Health check funcionando
- ✅ Endpoints PIX disponíveis
- ⚠️ Necessário configurar MASTER_PAGAMENTOS_SECRET_KEY no ambiente de produção

## Próximos Passos

1. **Configurar chave do gateway**: Você precisa obter uma chave válida da MasterPagamentosBR e configurar a variável `MASTER_PAGAMENTOS_SECRET_KEY` no ambiente de produção.

2. **Testar com chave real**: Com a chave válida, teste a criação de pagamentos PIX reais.

3. **Integrar com o bot**: Use a URL `https://p9hwiqcnqlp5.manus.space` no seu bot Telegram.

4. **Configurar webhook**: Configure o webhook no painel da MasterPagamentosBR para apontar para `https://p9hwiqcnqlp5.manus.space/api/pix/webhook`.

## Exemplo de Teste

```bash
# Testar criação de pagamento
curl -X POST https://p9hwiqcnqlp5.manus.space/api/pix/create_payment \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn" \
  -d '{"user_id": 123456, "plan_type": "lifetime"}'

# Testar verificação de status
curl -X GET https://p9hwiqcnqlp5.manus.space/api/pix/check_payment_status/test-payment-123 \
  -H "X-API-Key: sk_live_v2qKajzeM7XuklbSlGTVFLHWljkOBPka0LNj0wlUpn"
```

