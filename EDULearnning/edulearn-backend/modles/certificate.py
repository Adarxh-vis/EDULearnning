from bson import ObjectId
from extensions import mongo
from datetime import datetime
import random
import string

class Certificate:
    def __init__(self, userId, courseId, courseTitle, userName, instructorName, completionDate=None):
        self.userId = userId
        self.courseId = courseId
        self.courseTitle = courseTitle
        self.userName = userName
        self.instructorName = instructorName
        self.certificateId = self.generate_certificate_id()
        self.verificationCode = self.generate_verification_code()
        self.issueDate = completionDate or datetime.utcnow()
        self.createdAt = datetime.utcnow()

    @staticmethod
    def generate_certificate_id():
        """Generate unique certificate ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"CERT-{timestamp}-{random_str}"

    @staticmethod
    def generate_verification_code():
        """Generate verification code for certificate authenticity"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def save(self):
        certificate_data = {
            'userId': self.userId,
            'courseId': self.courseId,
            'courseTitle': self.courseTitle,
            'userName': self.userName,
            'instructorName': self.instructorName,
            'certificateId': self.certificateId,
            'verificationCode': self.verificationCode,
            'issueDate': self.issueDate,
            'createdAt': self.createdAt
        }
        result = mongo.db.certificates.insert_one(certificate_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(cert_id):
        try:
            return mongo.db.certificates.find_one({'_id': ObjectId(cert_id)})
        except:
            return None

    @staticmethod
    def find_by_certificate_id(certificate_id):
        return mongo.db.certificates.find_one({'certificateId': certificate_id})

    @staticmethod
    def find_by_verification_code(verification_code):
        return mongo.db.certificates.find_one({'verificationCode': verification_code})

    @staticmethod
    def find_by_user(user_id):
        return list(mongo.db.certificates.find({'userId': user_id}).sort('issueDate', -1))

    @staticmethod
    def find_by_user_and_course(user_id, course_id):
        return mongo.db.certificates.find_one({
            'userId': user_id,
            'courseId': course_id
        })

    @staticmethod
    def check_eligibility(user_id, course_id):
        """Check if user is eligible for certificate"""
        from modles.test_result import TestResult
        
        # Check if certificate already exists
        existing_cert = Certificate.find_by_user_and_course(user_id, course_id)
        if existing_cert:
            return False, "Certificate already issued for this course"
        
        # Check if all assessments are passed
        all_passed = TestResult.check_all_assessments_passed(user_id, course_id)
        if not all_passed:
            return False, "Not all assessments have been passed"
        
        return True, "Eligible for certificate"

    @staticmethod
    def generate_for_user(user_id, course_id, course_title, user_name, instructor_name):
        """Generate certificate for user after validation"""
        eligible, message = Certificate.check_eligibility(user_id, course_id)
        
        if not eligible:
            return None, message
        
        certificate = Certificate(
            userId=user_id,
            courseId=course_id,
            courseTitle=course_title,
            userName=user_name,
            instructorName=instructor_name
        )
        
        cert_id = certificate.save()
        return cert_id, "Certificate generated successfully"

    @staticmethod
    def verify_certificate(certificate_id=None, verification_code=None):
        """Verify certificate authenticity"""
        if certificate_id:
            cert = Certificate.find_by_certificate_id(certificate_id)
        elif verification_code:
            cert = Certificate.find_by_verification_code(verification_code)
        else:
            return False, "No certificate ID or verification code provided"
        
        if cert:
            return True, {
                'valid': True,
                'userName': cert.get('userName'),
                'courseTitle': cert.get('courseTitle'),
                'issueDate': cert.get('issueDate'),
                'certificateId': cert.get('certificateId')
            }
        
        return False, "Certificate not found or invalid"

    @staticmethod
    def find_all(filter_query=None):
        if filter_query is None:
            filter_query = {}
        return list(mongo.db.certificates.find(filter_query))
