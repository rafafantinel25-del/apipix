import os
import base64
import hashlib
import hmac
from typing import Dict, Tuple


def get_api_key_from_headers(headers: Dict[str, str]) -> Tuple[bool, str]:
    """
    Extract API key from headers supporting both X-API-Key and Authorization: Bearer <key>.
    Returns tuple (found, key or reason).
    """
    # Normalize header keys
    normalized = {k.lower(): v for k, v in headers.items()}

    # Prefer X-API-Key
    api_key = normalized.get('x-api-key') or normalized.get('x_api_key')
    if api_key:
        return True, api_key.strip()

    # Fallback to Authorization Bearer
    auth = normalized.get('authorization')
    if auth and auth.lower().startswith('bearer '):
        return True, auth.split(' ', 1)[1].strip()

    return False, 'Missing API key. Provide X-API-Key or Authorization: Bearer <key>'


def is_valid_api_key(key: str) -> bool:
    # Support multiple keys via PIX_API_KEYS (comma-separated), fallback to PIX_API_KEY
    keys_csv = os.getenv('PIX_API_KEYS')
    candidates: list[str] = []
    if keys_csv:
        candidates.extend([k.strip() for k in keys_csv.split(',') if k.strip()])
    fallback = os.getenv('PIX_API_KEY') or os.getenv('MASTER_PAGAMENTOS_SECRET_KEY')
    if fallback:
        candidates.append(fallback.strip())
    # No configured keys -> allow for local dev
    if not candidates:
        return True
    provided = key.strip()
    return any(provided == c for c in candidates)


PLANS = {
    '7_days': 1500,
    '15_days': 2990,
    '30_days': 4990,
    'lifetime': 1997,
}

def resolve_amount(plan_type: str, amount: int | None) -> Tuple[bool, int, str | None]:
    if amount is not None:
        return True, int(amount), None
    if plan_type in PLANS:
        return True, PLANS[plan_type], None
    return False, 0, 'Invalid plan_type and amount not provided'

