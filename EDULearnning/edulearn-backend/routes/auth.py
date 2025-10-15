from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from modles.user import User

auth = Blueprint('auth', __name__)

@auth.route('/student/signup', methods=['POST'])
def student_signup():
    data = request.get_json() or {}
    fullName = data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not fullName or not email or not password:
        return jsonify({'message': 'fullName, email, and password are required'}), 400

    if User.find_by_email(email):
        return jsonify({'message': 'User already exists'}), 400

    user = User(fullName, email, password, role='student')
    user_id = user.save()
    access_token = create_access_token(identity=str(user_id))

    return jsonify({'token': access_token, 'user': {'_id': user_id, 'fullName': fullName, 'email': email, 'role': 'student'}}), 201

@auth.route('/teacher/signup', methods=['POST'])
def teacher_signup():
    data = request.get_json() or {}
    fullName = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    subject = data.get('subject')
    qualification = data.get('qualification')
    experience = data.get('experience')

    if not all([fullName, email, password, subject, qualification, experience]):
        return jsonify({'message': 'All fields are required'}), 400

    if User.find_by_email(email):
        return jsonify({'message': 'User already exists'}), 400

    user = User(fullName, email, password, role='teacher')
    user.subject = subject
    user.qualification = qualification
    user.experience = experience
    user_id = user.save()
    access_token = create_access_token(identity=str(user_id))

    return jsonify({'token': access_token, 'user': {'_id': user_id, 'fullName': fullName, 'email': email, 'role': 'teacher'}}), 201

@auth.route('/admin/signup', methods=['POST'])
def admin_signup():
    data = request.get_json() or {}
    fullName = data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not fullName or not email or not password:
        return jsonify({'message': 'fullName, email, and password are required'}), 400

    if User.find_by_email(email):
        return jsonify({'message': 'User already exists'}), 400

    user = User(fullName, email, password, role='admin')
    user_id = user.save()
    access_token = create_access_token(identity=str(user_id))

    return jsonify({'token': access_token, 'user': {'_id': user_id, 'fullName': fullName, 'email': email, 'role': 'admin'}}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.find_by_email(email)
    if user and User.verify_password(user['password'], password):
        from datetime import datetime
        User.update_by_id(str(user['_id']), {'lastLogin': datetime.utcnow()})
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({'token': access_token, 'user': {'_id': str(user['_id']), 'fullName': user['fullName'], 'email': user['email'], 'role': user['role']}}), 200

    return jsonify({'message': 'Invalid email or password'}), 401
