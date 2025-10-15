from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.test_result import TestResult
from modles.assessment import Assessment
from utils.serializers import serialize_list, to_str_id
from datetime import datetime

test_results = Blueprint('test_results', __name__)

@test_results.route('/submit', methods=['POST'])
@jwt_required()
def submit_test():
    """Submit test answers and calculate score"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['assessmentId', 'answers']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        assessment_id = data['assessmentId']
        user_answers = data['answers']
        time_spent = data.get('timeSpent')
        
        # Get assessment
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404
        
        # Calculate score for MCQ
        if assessment['type'] == 'mcq':
            score, passed = calculate_mcq_score(
                assessment['questions'],
                user_answers,
                assessment['passingScore']
            )
        else:
            # For assignments, score will be set by instructor later
            score = 0
            passed = False
        
        # Save test result
        test_result = TestResult(
            userId=user_id,
            assessmentId=assessment_id,
            courseId=assessment['courseId'],
            answers=user_answers,
            score=score,
            passed=passed,
            timeSpent=time_spent
        )
        
        result_id = test_result.save()
        
        return jsonify({
            '_id': result_id,
            'score': score,
            'passed': passed,
            'passingScore': assessment['passingScore'],
            'message': 'Test submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error submitting test: {str(e)}'}), 500

def calculate_mcq_score(questions, user_answers, passing_score):
    """Calculate score for MCQ assessment"""
    if not questions or not user_answers:
        return 0, False
    
    total_questions = len(questions)
    correct_answers = 0
    
    # Create a map of question IDs to correct answers
    correct_answer_map = {}
    for question in questions:
        question_id = str(question.get('id') or question.get('_id', ''))
        correct_answer_map[question_id] = question.get('correctAnswer')
    
    # Check user answers
    for answer in user_answers:
        question_id = str(answer.get('questionId', ''))
        user_answer = answer.get('answer')
        
        if question_id in correct_answer_map:
            if user_answer == correct_answer_map[question_id]:
                correct_answers += 1
    
    # Calculate percentage score
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= passing_score
    
    return round(score, 2), passed

@test_results.route('/user/<user_id>/course/<course_id>', methods=['GET'])
@jwt_required()
def get_user_course_results(user_id, course_id):
    """Get all test results for a user in a specific course"""
    try:
        current_user = get_jwt_identity()
        
        # Users can only view their own results
        if current_user != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        results = TestResult.find_by_user_and_course(user_id, course_id)
        return jsonify(serialize_list(results)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching results: {str(e)}'}), 500

@test_results.route('/assessment/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment_results(assessment_id):
    """Get user's results for a specific assessment"""
    try:
        user_id = get_jwt_identity()
        
        results = TestResult.find_by_user_and_assessment(user_id, assessment_id)
        return jsonify(serialize_list(results)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching results: {str(e)}'}), 500

@test_results.route('/best-score/<assessment_id>', methods=['GET'])
@jwt_required()
def get_best_score(assessment_id):
    """Get user's best score for an assessment"""
    try:
        user_id = get_jwt_identity()
        
        best_result = TestResult.get_best_score(user_id, assessment_id)
        
        if not best_result:
            return jsonify({'message': 'No results found'}), 404
        
        return jsonify(to_str_id(best_result)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching best score: {str(e)}'}), 500

@test_results.route('/course-summary/<course_id>', methods=['GET'])
@jwt_required()
def get_course_summary(course_id):
    """Get summary of all assessment results for a course"""
    try:
        user_id = get_jwt_identity()
        
        summary = TestResult.get_course_assessment_summary(user_id, course_id)
        
        # Calculate overall completion
        total_assessments = len(summary)
        passed_assessments = sum(1 for item in summary if item['passed'])
        
        return jsonify({
            'summary': summary,
            'totalAssessments': total_assessments,
            'passedAssessments': passed_assessments,
            'allPassed': passed_assessments == total_assessments,
            'completionPercentage': (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching course summary: {str(e)}'}), 500

@test_results.route('/check-eligibility/<course_id>', methods=['GET'])
@jwt_required()
def check_certificate_eligibility(course_id):
    """Check if user is eligible for certificate"""
    try:
        user_id = get_jwt_identity()
        
        all_passed = TestResult.check_all_assessments_passed(user_id, course_id)
        
        return jsonify({
            'eligible': all_passed,
            'message': 'Eligible for certificate' if all_passed else 'Complete all assessments to earn certificate'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error checking eligibility: {str(e)}'}), 500

@test_results.route('/<result_id>', methods=['GET'])
@jwt_required()
def get_result_details(result_id):
    """Get detailed result information"""
    try:
        user_id = get_jwt_identity()
        
        result = TestResult.find_by_id(result_id)
        if not result:
            return jsonify({'message': 'Result not found'}), 404
        
        # Users can only view their own results
        if result.get('userId') != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        return jsonify(to_str_id(result)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching result: {str(e)}'}), 500

@test_results.route('/grade-assignment/<result_id>', methods=['PUT'])
@jwt_required()
def grade_assignment(result_id):
    """Grade an assignment submission (instructor only)"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        
        # Validate required fields
        if 'score' not in data:
            return jsonify({'message': 'Score is required'}), 400
        
        score = data['score']
        if not (0 <= score <= 100):
            return jsonify({'message': 'Score must be between 0 and 100'}), 400
        
        # Get result
        result = TestResult.find_by_id(result_id)
        if not result:
            return jsonify({'message': 'Result not found'}), 404
        
        # Get assessment to verify instructor
        assessment = Assessment.find_by_id(result['assessmentId'])
        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404
        
        # Verify user is the course instructor
        from modles.course import Course
        course = Course.find_by_id(assessment['courseId'])
        if not course or course.get('instructor') != user_id:
            return jsonify({'message': 'Only course instructor can grade assignments'}), 403
        
        # Update score and passed status
        passed = score >= assessment['passingScore']
        update_data = {
            'score': score,
            'passed': passed,
            'gradedBy': user_id,
            'gradedAt': datetime.utcnow(),
            'feedback': data.get('feedback', '')
        }
        
        from bson import ObjectId
        from extensions import mongo
        mongo.db.test_results.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'message': 'Assignment graded successfully',
            'score': score,
            'passed': passed
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error grading assignment: {str(e)}'}), 500
