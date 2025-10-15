from bson import ObjectId
from extensions import mongo
from datetime import datetime

class Assessment:
    def __init__(self, courseId, moduleId, title, type, questions, passingScore, timeLimit=None, instructions=None):
        self.courseId = courseId
        self.moduleId = moduleId
        self.title = title
        self.type = type  # 'mcq' or 'assignment'
        self.questions = questions  # Array of question objects
        self.passingScore = passingScore  # Percentage required to pass
        self.timeLimit = timeLimit  # Time limit in minutes (optional)
        self.instructions = instructions
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()

    def save(self):
        assessment_data = {
            'courseId': self.courseId,
            'moduleId': self.moduleId,
            'title': self.title,
            'type': self.type,
            'questions': self.questions,
            'passingScore': self.passingScore,
            'timeLimit': self.timeLimit,
            'instructions': self.instructions,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
        result = mongo.db.assessments.insert_one(assessment_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(assessment_id):
        try:
            return mongo.db.assessments.find_one({'_id': ObjectId(assessment_id)})
        except:
            return None

    @staticmethod
    def find_by_course(course_id):
        return list(mongo.db.assessments.find({'courseId': course_id}))

    @staticmethod
    def find_by_module(course_id, module_id):
        return list(mongo.db.assessments.find({'courseId': course_id, 'moduleId': module_id}))

    @staticmethod
    def update_by_id(assessment_id, update_data):
        update_data['updatedAt'] = datetime.utcnow()
        result = mongo.db.assessments.update_one(
            {'_id': ObjectId(assessment_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_by_id(assessment_id):
        result = mongo.db.assessments.delete_one({'_id': ObjectId(assessment_id)})
        return result.deleted_count > 0

    @staticmethod
    def find_all(filter_query=None):
        if filter_query is None:
            filter_query = {}
        return list(mongo.db.assessments.find(filter_query))
