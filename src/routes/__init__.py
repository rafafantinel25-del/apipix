from flask import Blueprint

pix_bp = Blueprint('pix', __name__)
user_bp = Blueprint('user', __name__)
health_bp = Blueprint('health', __name__)

from . import pix, user, health  # noqa: E402,F401

