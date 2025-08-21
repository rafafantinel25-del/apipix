from flask import request, jsonify
from . import pix_bp
from ..services.pix_service import get_api_key_from_headers, is_valid_api_key, resolve_amount
from ..models.payment import Payment
from ..models.base import db


def _extract_payload(data: dict) -> tuple[bool, dict, str | None]:
    """Accept both API format and bot format. Return normalized payload.
    Supported inputs:
      - {user_id, plan_type}
      - {user_id, plan_type, amount}
      - Bot style: {amount, paymentMethod, description, external_id, customer, items}
    """
    if not isinstance(data, dict):
        return False, {}, 'Invalid JSON payload'

    # Preferred: explicit user_id and plan_type
    user_id = data.get('user_id') or data.get('telegram_user_id')
    plan_type = data.get('plan_type')
    amount = data.get('amount')

    # If missing requireds, try to infer from bot style
    if not user_id or not plan_type:
        meta = data.get('metadata') or {}
        user_id = user_id or meta.get('user_id')
        plan_type = plan_type or meta.get('plan_type')
        # Fallbacks for common bot payloads
        # user_id may come as external_id
        user_id = user_id or data.get('external_id')
        # plan_type may be deduced from description or first item title
        maybe_text = data.get('description')
        items = data.get('items') or []
        if not maybe_text and isinstance(items, list) and items:
            first = items[0] or {}
            maybe_text = first.get('title')
        if isinstance(maybe_text, str):
            lower = maybe_text.lower()
            if '7' in lower and ('7 dias' in lower or '7 days' in lower or '7_' in lower):
                plan_type = plan_type or '7_days'
            elif '15' in lower:
                plan_type = plan_type or '15_days'
            elif '30' in lower:
                plan_type = plan_type or '30_days'
            elif 'vital' in lower or 'life' in lower:
                plan_type = plan_type or 'lifetime'

    if not user_id or not plan_type:
        return False, {}, 'Missing required fields: user_id, plan_type'

    ok, resolved_amount, reason = resolve_amount(plan_type, amount)
    if not ok:
        return False, {}, reason

    normalized = {
        'user_id': str(user_id),
        'plan_type': plan_type,
        'amount': resolved_amount,
        'description': data.get('description') or f'Assinatura VIP - {plan_type}',
        'external_id': data.get('external_id'),
    }
    return True, normalized, None


@pix_bp.route('/create_payment', methods=['POST'])
def create_payment():
    # Auth
    found, key_or_reason = get_api_key_from_headers(request.headers)
    if not found:
        return jsonify({'error': 'Unauthorized', 'message': key_or_reason}), 401
    if not is_valid_api_key(key_or_reason):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401

    data = request.get_json(silent=True) or {}
    ok, payload, reason = _extract_payload(data)
    if not ok:
        return jsonify({'error': 'Bad Request', 'message': reason}), 400

    payment = Payment(
        user_id=payload['user_id'],
        plan_type=payload['plan_type'],
        amount=payload['amount'],
        status='pending',
    )
    db.session.add(payment)
    db.session.commit()

    # Fake PIX fields for now
    response = {
        'success': True,
        'payment_id': payment.id,
        'pix_code': f'PIX-{payment.id}',
        'qr_code': f'https://example.com/qr/{payment.id}',
        'amount': payment.amount,
        'expires_at': payment.expires_at.isoformat(),
    }
    return jsonify(response), 200


@pix_bp.route('/check_payment_status/<payment_id>', methods=['GET'])
def check_payment_status(payment_id: str):
    # Auth
    found, key_or_reason = get_api_key_from_headers(request.headers)
    if not found:
        return jsonify({'error': 'Unauthorized', 'message': key_or_reason}), 401
    if not is_valid_api_key(key_or_reason):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({
        'payment_id': payment.id,
        'status': payment.status,
        'user_id': payment.user_id,
        'plan_type': payment.plan_type,
        'amount': payment.amount,
    })


@pix_bp.route('/webhook', methods=['POST'])
def webhook():
    # Optionally validate signature here
    data = request.get_json(silent=True) or {}
    payment_id = data.get('payment_id')
    status = data.get('status')
    if not payment_id or not status:
        return jsonify({'error': 'Bad Request', 'message': 'Missing field'}), 400
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Not Found'}), 404
    payment.status = status
    db.session.commit()
    return jsonify({'ok': True})

