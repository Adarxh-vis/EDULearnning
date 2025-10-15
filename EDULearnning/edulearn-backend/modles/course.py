from bson import ObjectId
from extensions import mongo

class Course:
    def __init__(self, title, description, category, instructor, price):
        self.title = title
        self.description = description
        self.category = category
        self.instructor = instructor
        self.price = price
        self.isPublished = False

    def save(self):
        course_data = {
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'instructor': self.instructor,
            'price': self.price,
            'isPublished': self.isPublished
        }
        result = mongo.db.courses.insert_one(course_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(course_id):
        return mongo.db.courses.find_one({'_id': ObjectId(course_id)})

    @staticmethod
    def find_all(filter_query=None):
        if filter_query is None:
            filter_query = {}
        return list(mongo.db.courses.find(filter_query))

