from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.course import Course
from utils.serializers import serialize_list, to_str_id
from bson import ObjectId
from extensions import mongo

courses = Blueprint('courses', __name__)

@courses.route('/', methods=['GET'])
def list_courses():
    docs = Course.find_all()
    return jsonify(serialize_list(docs)), 200

@courses.route('/', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    price = data.get('price')
    instructor = get_jwt_identity()  # Get the current user's ID

    if not title or not description or not category or price is None:
        return jsonify({'message': 'title, description, category, and price are required'}), 400

    course = Course(title, description, category, instructor, price)
    course_id = course.save()
    return jsonify({'_id': course_id, 'title': title, 'instructor': instructor}), 201

@courses.route('/my', methods=['GET'])
@jwt_required()
def get_my_courses():
    instructor_id = get_jwt_identity()
    docs = Course.find_all({'instructor': instructor_id})
    return jsonify(serialize_list(docs)), 200

@courses.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        doc = Course.find_by_id(course_id)
    except Exception:
        doc = None

    # If not found by ObjectId, try to find by courseId field
    if not doc:
        doc = mongo.db.courses.find_one({'courseId': course_id})

    if not doc:
        return jsonify({'message': 'Course not found'}), 404
    return jsonify(to_str_id(doc)), 200

@courses.route('/user', methods=['GET'])
@jwt_required()
def get_user_courses():
    user_id = get_jwt_identity()
    docs = Course.find_all()
    return jsonify(serialize_list(docs)), 200
