from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.assessment import Assessment
from modles.course import Course
from utils.serializers import serialize_list, to_str_id
from bson import ObjectId

assessments = Blueprint('assessments', __name__)

@assessments.route('/course/<course_id>', methods=['GET'])
def get_course_assessments(course_id):
    """Get all assessments for a specific course"""
    try:
        assessments_list = Assessment.find_by_course(course_id)
        return jsonify(serialize_list(assessments_list)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching assessments: {str(e)}'}), 500

@assessments.route('/module/<course_id>/<module_id>', methods=['GET'])
def get_module_assessments(course_id, module_id):
    """Get all assessments for a specific module"""
    try:
        assessments_list = Assessment.find_by_module(course_id, module_id)
        return jsonify(serialize_list(assessments_list)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching assessments: {str(e)}'}), 500

@assessments.route('/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    """Get a specific assessment by ID"""
    try:
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404
        return jsonify(to_str_id(assessment)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching assessment: {str(e)}'}), 500

@assessments.route('/', methods=['POST'])
@jwt_required()
def create_assessment():
    """Create a new assessment (instructor only)"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['courseId', 'moduleId', 'title', 'type', 'questions', 'passingScore']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verify user is the course instructor
        course = Course.find_by_id(data['courseId'])
        if not course:
            return jsonify({'message': 'Course not found'}), 404
        
        if course.get('instructor') != user_id:
            return jsonify({'message': 'Only course instructor can create assessments'}), 403
        
        # Validate assessment type
        if data['type'] not in ['mcq', 'assignment']:
            return jsonify({'message': 'Invalid assessment type. Must be "mcq" or "assignment"'}), 400
        
        # Validate passing score
        if not (0 <= data['passingScore'] <= 100):
            return jsonify({'message': 'Passing score must be between 0 and 100'}), 400
        
        # Create assessment
        assessment = Assessment(
            courseId=data['courseId'],
            moduleId=data['moduleId'],
            title=data['title'],
            type=data['type'],
            questions=data['questions'],
            passingScore=data['passingScore'],
            timeLimit=data.get('timeLimit'),
            instructions=data.get('instructions')
        )
        
        assessment_id = assessment.save()
        return jsonify({
            '_id': assessment_id,
            'message': 'Assessment created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating assessment: {str(e)}'}), 500

@assessments.route('/<assessment_id>', methods=['PUT'])
@jwt_required()
def update_assessment(assessment_id):
    """Update an existing assessment (instructor only)"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        
        # Get assessment
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404
        
        # Verify user is the course instructor
        course = Course.find_by_id(assessment['courseId'])
        if not course or course.get('instructor') != user_id:
            return jsonify({'message': 'Only course instructor can update assessments'}), 403
        
        # Prepare update data
        update_data = {}
        allowed_fields = ['title', 'questions', 'passingScore', 'timeLimit', 'instructions']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Validate passing score if provided
        if 'passingScore' in update_data:
            if not (0 <= update_data['passingScore'] <= 100):
                return jsonify({'message': 'Passing score must be between 0 and 100'}), 400
        
        # Update assessment
        success = Assessment.update_by_id(assessment_id, update_data)
        
        if success:
            return jsonify({'message': 'Assessment updated successfully'}), 200
        else:
            return jsonify({'message': 'No changes made'}), 200
            
    except Exception as e:
        return jsonify({'message': f'Error updating assessment: {str(e)}'}), 500

@assessments.route('/<assessment_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment(assessment_id):
    """Delete an assessment (instructor only)"""
    try:
        user_id = get_jwt_identity()
        
        # Get assessment
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404
        
        # Verify user is the course instructor
        course = Course.find_by_id(assessment['courseId'])
        if not course or course.get('instructor') != user_id:
            return jsonify({'message': 'Only course instructor can delete assessments'}), 403
        
        # Delete assessment
        success = Assessment.delete_by_id(assessment_id)
        
        if success:
            return jsonify({'message': 'Assessment deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete assessment'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error deleting assessment: {str(e)}'}), 500

@assessments.route('/all', methods=['GET'])
@jwt_required()
def get_all_assessments():
    """Get all assessments (admin only)"""
    try:
        assessments_list = Assessment.find_all()
        return jsonify(serialize_list(assessments_list)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching assessments: {str(e)}'}), 500
