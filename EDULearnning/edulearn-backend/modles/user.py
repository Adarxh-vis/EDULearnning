from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import mongo

class User:
    def __init__(self, fullName, email, password, role='student'):
        self.fullName = fullName
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role
        self.isVerified = False
        self.createdAt = None
        self.updatedAt = None
        self.lastLogin = None
        # Teacher-specific fields
        self.subject = None
        self.qualification = None
        self.experience = None

    def save(self):
        user_data = {
            'fullName': self.fullName,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'isVerified': self.isVerified,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'lastLogin': self.lastLogin
        }
        # Add teacher-specific fields if they exist
        if self.subject:
            user_data['subject'] = self.subject
        if self.qualification:
            user_data['qualification'] = self.qualification
        if self.experience:
            user_data['experience'] = self.experience

        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)

    @staticmethod
    def update_by_id(user_id, update_data):
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
