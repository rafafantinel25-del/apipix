from flask import request, jsonify
from . import user_bp

@user_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "User routes OK"})

