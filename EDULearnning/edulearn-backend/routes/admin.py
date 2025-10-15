from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.user import User
from bson import ObjectId
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to check if user is admin"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        role_filter = request.args.get('role')
        search = request.args.get('search')

        # Build query
        query = {}
        if role_filter:
            query['role'] = role_filter
        if search:
            query['$or'] = [
                {'fullName': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]

        # Get users with pagination
        users = User.find_all(query, skip=(page-1)*limit, limit=limit)
        total = User.count(query)

        # Format response
        user_list = []
        for user in users:
            user_list.append({
                '_id': str(user['_id']),
                'fullName': user['fullName'],
                'email': user['email'],
                'role': user['role'],
                'createdAt': user.get('createdAt'),
                'lastLogin': user.get('lastLogin'),
                'isActive': user.get('isActive', True)
            })

        return jsonify({
            'users': user_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching users: {str(e)}'}), 500

@admin.route('/users/<user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get specific user details"""
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            '_id': str(user['_id']),
            'fullName': user['fullName'],
            'email': user['email'],
            'role': user['role'],
            'createdAt': user.get('createdAt'),
            'lastLogin': user.get('lastLogin'),
            'isActive': user.get('isActive', True)
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching user: {str(e)}'}), 500

@admin.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details"""
    try:
        data = request.get_json()
        allowed_fields = ['fullName', 'email', 'role', 'isActive']

        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'message': 'No valid fields to update'}), 400

        # Check if email is being changed and if it's already taken
        if 'email' in update_data:
            existing_user = User.find_by_email(update_data['email'])
            if existing_user and str(existing_user['_id']) != user_id:
                return jsonify({'message': 'Email already in use'}), 400

        result = User.update_by_id(user_id, update_data)
        if result.modified_count == 0:
            return jsonify({'message': 'User not found or no changes made'}), 404

        return jsonify({'message': 'User updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Error updating user: {str(e)}'}), 500

@admin.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (soft delete by setting isActive to false)"""
    try:
        # Instead of hard delete, we'll soft delete
        result = User.update_by_id(user_id, {'isActive': False})
        if result.modified_count == 0:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({'message': 'User deactivated successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Error deleting user: {str(e)}'}), 500

@admin.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        total_users = User.count({})
        active_users = User.count({'isActive': True})
        students = User.count({'role': 'student'})
        teachers = User.count({'role': 'teacher'})
        admins = User.count({'role': 'admin'})

        return jsonify({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'students': students,
            'teachers': teachers,
            'admins': admins
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching stats: {str(e)}'}), 500
