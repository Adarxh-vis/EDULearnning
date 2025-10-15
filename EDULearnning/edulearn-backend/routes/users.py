from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.user import User
from extensions import mongo
from bson import ObjectId
from utils.serializers import to_str_id

users = Blueprint('users', __name__)

@users.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    if user:
        return jsonify({
            '_id': str(user['_id']),
            'fullName': user.get('fullName'),
            'email': user.get('email'),
            'role': user.get('role', 'student')
        }), 200
    return jsonify({'message': 'User not found'}), 404

@users.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}

    updates = {}
    if 'fullName' in data and data['fullName']:
        updates['fullName'] = data['fullName']
    if 'email' in data and data['email']:
        updates['email'] = data['email']

    if not updates:
        return jsonify({'message': 'No valid fields to update'}), 400

    result = mongo.db.users.update_one({'_id': ObjectId(current_user_id)}, {'$set': updates})
    if result.matched_count:
        updated = User.find_by_id(current_user_id)
        return jsonify(to_str_id(updated)), 200

    return jsonify({'message': 'User not found'}), 404
