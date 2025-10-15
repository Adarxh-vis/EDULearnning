from bson import ObjectId
from extensions import mongo
from datetime import datetime

class TestResult:
    def __init__(self, userId, assessmentId, courseId, answers, score, passed, timeSpent=None):
        self.userId = userId
        self.assessmentId = assessmentId
        self.courseId = courseId
        self.answers = answers  # Array of user's answers
        self.score = score  # Percentage score
        self.passed = passed  # Boolean
        self.timeSpent = timeSpent  # Time spent in minutes
        self.attemptDate = datetime.utcnow()

    def save(self):
        result_data = {
            'userId': self.userId,
            'assessmentId': self.assessmentId,
            'courseId': self.courseId,
            'answers': self.answers,
            'score': self.score,
            'passed': self.passed,
            'timeSpent': self.timeSpent,
            'attemptDate': self.attemptDate
        }
        result = mongo.db.test_results.insert_one(result_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(result_id):
        try:
            return mongo.db.test_results.find_one({'_id': ObjectId(result_id)})
        except:
            return None

    @staticmethod
    def find_by_user_and_course(user_id, course_id):
        return list(mongo.db.test_results.find({
            'userId': user_id,
            'courseId': course_id
        }).sort('attemptDate', -1))

    @staticmethod
    def find_by_user_and_assessment(user_id, assessment_id):
        return list(mongo.db.test_results.find({
            'userId': user_id,
            'assessmentId': assessment_id
        }).sort('attemptDate', -1))

    @staticmethod
    def get_best_score(user_id, assessment_id):
        results = mongo.db.test_results.find({
            'userId': user_id,
            'assessmentId': assessment_id
        }).sort('score', -1).limit(1)
        
        results_list = list(results)
        return results_list[0] if results_list else None

    @staticmethod
    def check_all_assessments_passed(user_id, course_id):
        """Check if user has passed all assessments for a course"""
        from modles.assessment import Assessment
        
        # Get all assessments for the course
        assessments = Assessment.find_by_course(course_id)
        
        if not assessments:
            return True  # No assessments required
        
        # Check if user has passed each assessment
        for assessment in assessments:
            assessment_id = str(assessment['_id'])
            best_result = TestResult.get_best_score(user_id, assessment_id)
            
            if not best_result or not best_result.get('passed', False):
                return False
        
        return True

    @staticmethod
    def get_course_assessment_summary(user_id, course_id):
        """Get summary of all assessment results for a course"""
        from modles.assessment import Assessment
        
        assessments = Assessment.find_by_course(course_id)
        summary = []
        
        for assessment in assessments:
            assessment_id = str(assessment['_id'])
            best_result = TestResult.get_best_score(user_id, assessment_id)
            
            summary.append({
                'assessmentId': assessment_id,
                'assessmentTitle': assessment.get('title'),
                'type': assessment.get('type'),
                'passingScore': assessment.get('passingScore'),
                'bestScore': best_result.get('score') if best_result else None,
                'passed': best_result.get('passed') if best_result else False,
                'attempts': len(TestResult.find_by_user_and_assessment(user_id, assessment_id))
            })
        
        return summary

    @staticmethod
    def find_all(filter_query=None):
        if filter_query is None:
            filter_query = {}
        return list(mongo.db.test_results.find(filter_query))
