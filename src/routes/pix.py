from flask import Blueprint, request, jsonify, current_app as cuurrent_app
import os
import requests
import json
import base64
import re
from datetime import datetime, timedelta
from src.models.payment import Payment
from src.models.user import User
from src.extensions import db, limiter
import redis

pix_bp = Blueprint("pix", __name__)

redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True
)

class PixService:
    def __init__(self):
        self.api_url = os.getenv(
            "MASTER_PAGAMENTOS_API_URL", "https://api.masterpagamentosbr.com/v1"
        )
        self.purchase_url = os.getenv(
            "MASTER_PAGAMENTOS_PURCHASE_URL",
            "https://api.masterpagamentosbr.com/v1/transactions",
        )
        self.get_payment_url = os.getenv(
            "MASTER_PAGAMENTOS_GET_PAYMENT_URL",
            "https://api.masterpagamentosbr.com/v1/transactions/",
        )
        self.secret_key = os.getenv("MASTER_PAGAMENTOS_SECRET_KEY")
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def _get_auth_header(self):
        if not self.secret_key:
            return None
        auth_string = f"{self.secret_key}:x"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        header = f"Basic {encoded_auth}"
        return header
    
    def create_pix_payment(
        self, payment_id, amount, user_id, plan_type, customer_data=None
    ):
        try:
            auth_header = self._get_auth_header()
            if not auth_header:
                return {"error": "Authentication not configured"}
            
            plan_names = {
                "lifetime": "Acesso VIP Vitalício",
                "7_days": "Assinatura VIP - 7 dias",
                "15_days": "Assinatura VIP - 15 dias",
                "30_days": "Assinatura VIP - 30 dias",
                "special": "Oferta Especial",
            }
            
            if customer_data:
                customer = {
                    "name": customer_data.get("name", "Teste Local"),
                    "email": customer_data.get("email", "teste@exemplo.com"),
                    "phone": customer_data.get("phone", "11999999999"),
                    "document": {
                        "number": customer_data.get("document", {}).get(
                            "number", "13802749669"
                        ),
                        "type": customer_data.get("document", {}).get("type", "cpf"),
                    },
                }
            else:
                customer = {
                    "name": "Teste Local",
                    "email": "teste@exemplo.com",
                    "phone": "11999999999",
                    "document": {"number": "13802749669", "type": "cpf"},
                }
            
            transaction_data = {
                "amount": amount,
                "paymentMethod": "pix",
                "description": plan_names.get(plan_type, "Acesso VIP"),
                "external_id": payment_id,
                "customer": customer,
                "items": [
                    {
                        "title": plan_names.get(plan_type, "Acesso VIP"),
                        "unitPrice": amount,
                        "quantity": 1,
                        "tangible": False,
                    }
                ],
            }
            
            headers = {"Authorization": auth_header, "Content-Type": "application/json"}
            response = self.session.post(
                self.purchase_url, json=transaction_data, headers=headers, timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                pix_data = data.get("pix", {})
                return {
                    "success": True,
                    "transaction_id": data.get("id"),
                    "pix_code": pix_data.get("qrcode"),
                    "qr_code": data.get("secureUrl"),
                    "expires_at": pix_data.get("expirationDate"),
                    "customer_data": customer,
                }
            else:
                return {
                    "error": "Gateway error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                }
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com gateway: {e}")
            return {"error": "Connection error", "message": str(e)}
        except Exception as e:
            print(f"Erro inesperado ao criar pagamento: {e}")
            return {"error": "Unexpected error", "message": str(e)}
    
    def check_payment_status(self, transaction_id):
        cache_key = f"payment_status:{transaction_id}"
        cached_data = cuurrent_app.redis_client.get(cache_key)
        
        if cached_data:
            print(f"Status do pagamento {transaction_id} encontrado no cache")
            return json.loads(cached_data)
        
        try:
            auth_header = self._get_auth_header()
            if not auth_header:
                return {"error": "Authentication not configured"}
            
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            
            url = f"{self.get_payment_url}{transaction_id}"
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "success": True,
                    "status": data.get("status"),
                    "transaction_id": data.get("id"),
                    "amount": data.get("amount"),
                    "paid_at": data.get("paidAt"),
                }
                redis_client.setex(cache_key, 300, json.dumps(result))
                return result
            elif response.status_code == 404:
                return {"error": "Transaction not found"}
            else:
                print(f"Erro ao consultar transação: {response.status_code} - {response.text}")
                return {
                    "error": "Gateway error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                }
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com gateway: {e}")
            return {"error": "Connection error", "message": str(e)}
        except Exception as e:
            print(f"Erro inesperado ao consultar status: {e}")
            return {"error": "Unexpected error", "message": str(e)}

pix_service = PixService()

def _infer_user_and_plan(data: dict):
    user_id = data.get("user_id") or data.get("external_id")
    plan_type = data.get("plan_type")
    if not plan_type:
        text = data.get("description")
        items = data.get("items") or []
        if not text and items:
            text = (items[0] or {}).get("title")
        if isinstance(text, str):
            low = text.lower()
            if "7" in low:
                plan_type = "7_days"
            elif "15" in low:
                plan_type = "15_days"
            elif "30" in low:
                plan_type = "30_days"
            elif "vital" in low or "life" in low:
                plan_type = "lifetime"
    return user_id, plan_type

@pix_bp.route("/create_payment", methods=["POST"])
@limiter.limit("10 per minute")
def create_payment():
    auth_header = request.headers.get("Authorization")
    expected = os.getenv("MASTER_PAGAMENTOS_SECRET_KEY")
    if not auth_header and os.getenv("PIX_API_KEYS"):
        # Allow Authorization: Bearer <PIX_API_KEYS>
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            provided = auth_header.split(" ", 1)[1].strip()
            allowed = [k.strip() for k in os.getenv("PIX_API_KEYS").split(",") if k.strip()]
            if provided not in allowed:
                return jsonify({"error": "Unauthorized"}), 401
        else:
            return jsonify({"error": "Unauthorized"}), 401
    else:
        if not auth_header or auth_header != f"Bearer {expected}":
            return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    user_id, plan_type = _infer_user_and_plan(data)
    if not user_id or not plan_type:
        return jsonify({"error": "Missing required fields: user_id, plan_type"}), 400

    plan_prices = {
        "7_days": 1500,
        "15_days": 2500,
        "30_days": 4000,
        "lifetime": 10000,
        "special": 990,
    }
    amount = plan_prices.get(plan_type, 0)
    if amount == 0:
        return jsonify({"error": "Invalid plan type"}), 400

    import uuid
    payment_id = str(uuid.uuid4())
    result = pix_service.create_pix_payment(payment_id, amount, user_id, plan_type)
    if result.get("success"):
        try:
            expires_at = result.get("expires_at")
            if expires_at and isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            user = User.query.get(user_id)
            if not user:
                user = User(id=user_id, username=f"user_{user_id}", first_name="Test User")
                db.session.add(user)
                db.session.commit()
            new_payment = Payment(
                payment_id=payment_id,
                user_id=user_id,
                plan_type=plan_type,
                amount=amount,
                status="pending",
                pix_code=result.get("pix_code"),
                expires_at=expires_at,
            )
            db.session.add(new_payment)
            db.session.commit()
        except Exception as e:
            print(f"Erro ao salvar no banco de dados: {e}")
            return jsonify({"error": "Failed to save payment", "details": str(e)}), 500
        return jsonify(result)
    else:
        return jsonify(result), 400

@pix_bp.route("/check_payment_status/<payment_id>", methods=["GET"])
@limiter.limit("30 per minute")
def check_payment_status(payment_id):
    auth_header = request.headers.get("Authorization")
    expected_key = os.getenv("MASTER_PAGAMENTOS_SECRET_KEY")
    if not auth_header or auth_header != f"Bearer {expected_key}":
        return jsonify({"error": "Unauthorized"}), 401
    result = pix_service.check_payment_status(payment_id)
    if result.get("success"):
        try:
            payment = Payment.query.filter_by(payment_id=payment_id).first()
            if payment:
                old_status = payment.status
                new_status = result.get("status")
                if old_status != new_status:
                    payment.status = new_status
                    if new_status == "paid" and not payment.paid_at:
                        payment.paid_at = datetime.now()
                    db.session.commit()
        except Exception as e:
            print(f"Erro ao atualizar status no banco de dados: {e}")
        return jsonify(result)
    else:
        return jsonify(result), 400

@pix_bp.route("/generate_customer_data", methods=["GET"])
@limiter.limit("5 per minute")
def generate_customer_data():
    import random
    first_names = [
        "João", "Maria", "José", "Ana", "Carlos", "Paula", "Pedro", "Mariana",
    ]
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues", "Almeida",
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
    phone = f"21{random.randint(90000000, 99999999)}"
    
    def generate_valid_cpf():
        cpf = [random.randint(0, 9) for _ in range(9)]
        sum1 = sum((10 - i) * cpf[i] for i in range(9))
        digit1 = (sum1 * 10) % 11
        if digit1 == 10:
            digit1 = 0
        cpf.append(digit1)
        sum2 = sum((11 - i) * cpf[i] for i in range(10))
        digit2 = (sum2 * 10) % 11
        if digit2 == 10:
            digit2 = 0
        cpf.append(digit2)
        return f"{''.join(map(str, cpf[:3]))}.{''.join(map(str, cpf[3:6]))}.{''.join(map(str, cpf[6:9]))}-{''.join(map(str, cpf[9:11]))}"
    
    cpf_number = generate_valid_cpf()
    return jsonify(
        {
            "document": {
                "number": cpf_number.replace(".", "").replace("-", ""),
                "type": "cpf",
            },
            "email": email,
            "name": full_name,
            "phone": phone,
        }
    )

@pix_bp.route("/callback", methods=["POST"])
@limiter.limit("10 per minute")
def payment_callback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        transaction_id = data.get("id")
        status = data.get("status")
        if not transaction_id or not status:
            return jsonify({"error": "Invalid webhook data"}), 400
        payment = Payment.query.filter_by(payment_id=transaction_id).first()
        if not payment:
            return jsonify({"error": "Payment not found"}), 404
        payment.status = status
        if status == "paid" and not payment.paid_at:
            payment.paid_at = datetime.now()
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

