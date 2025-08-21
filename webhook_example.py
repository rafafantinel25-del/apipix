"""
Exemplo de Webhook para Integração PIX
Este arquivo mostra como implementar um webhook para receber notificações de pagamento PIX
"""

from flask import Flask, request, jsonify
import logging
import asyncio
from src.pix_integration import PixIntegration
from src.config import setup_logging

# Configurar logging
logger = setup_logging()

# Criar aplicação Flask
app = Flask(__name__)

# Instanciar integração PIX
pix_integration = PixIntegration()

@app.route('/webhook/pix', methods=['POST'])
def pix_webhook():
    """
    Endpoint para receber webhooks de pagamento PIX
    
    Exemplo de payload esperado:
    {
        "payment_id": "uuid-do-pagamento",
        "status": "paid",
        "amount": 1500,
        "paid_at": "2024-01-15T10:30:00Z",
        "payer": {
            "name": "João Silva",
            "document": "12345678901"
        }
    }
    """
    try:
        # Obter dados do webhook
        data = request.get_json()
        
        if not data:
            logger.error("Webhook recebido sem dados JSON")
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validar campos obrigatórios
        required_fields = ['payment_id', 'status']
        for field in required_fields:
            if field not in data:
                logger.error(f"Campo obrigatório ausente: {field}")
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        payment_id = data['payment_id']
        status = data['status']
        
        logger.info(f"Webhook recebido para pagamento {payment_id} com status {status}")
        
        # Processar webhook de forma assíncrona
        asyncio.create_task(process_webhook_async(data))
        
        # Retornar resposta imediata
        return jsonify({"status": "received", "payment_id": payment_id}), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

async def process_webhook_async(webhook_data):
    """Processa o webhook de forma assíncrona"""
    try:
        success = await pix_integration.process_webhook(webhook_data)
        
        if success:
            logger.info(f"Webhook processado com sucesso: {webhook_data['payment_id']}")
        else:
            logger.error(f"Falha ao processar webhook: {webhook_data['payment_id']}")
            
    except Exception as e:
        logger.error(f"Erro no processamento assíncrono do webhook: {e}")

@app.route('/webhook/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde"""
    return jsonify({
        "status": "healthy",
        "service": "PIX Webhook",
        "timestamp": "2024-01-15T10:30:00Z"
    })

@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Endpoint para testar o webhook"""
    test_data = {
        "payment_id": "test-payment-123",
        "status": "paid",
        "amount": 1500,
        "paid_at": "2024-01-15T10:30:00Z"
    }
    
    asyncio.create_task(process_webhook_async(test_data))
    
    return jsonify({
        "message": "Test webhook sent",
        "data": test_data
    })

if __name__ == '__main__':
    # Configurações para desenvolvimento
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

"""
INSTRUÇÕES DE USO:

1. Instalar Flask:
   pip install flask

2. Executar o webhook:
   python webhook_example.py

3. Configurar sua API PIX para enviar webhooks para:
   http://seu-servidor.com:5000/webhook/pix

4. Testar o webhook:
   curl -X POST http://localhost:5000/webhook/test

5. Verificar saúde:
   curl http://localhost:5000/webhook/health

CONFIGURAÇÃO EM PRODUÇÃO:

1. Use um servidor WSGI como Gunicorn:
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 webhook_example:app

2. Configure HTTPS com nginx ou similar

3. Adicione autenticação/validação de assinatura conforme sua API PIX

4. Configure logs apropriados para produção

5. Monitore o endpoint de saúde
"""

