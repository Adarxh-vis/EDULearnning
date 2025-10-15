from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from flask import jsonify
from modles.user import User

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        if user and user.get('role') == 'admin':
            return fn(*args, **kwargs)
        return jsonify({'message': 'Admin access required'}), 403
    return wrapper
