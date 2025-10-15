from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from modles.certificate import Certificate
from modles.course import Course
from modles.user import User
from utils.serializers import serialize_list, to_str_id
import io
from datetime import datetime

certificates = Blueprint('certificates', __name__)

@certificates.route('/generate', methods=['POST'])
@jwt_required()
def generate_certificate():
    """Generate certificate for a course after passing all assessments"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        
        # Validate required fields
        if 'courseId' not in data:
            return jsonify({'message': 'courseId is required'}), 400
        
        course_id = data['courseId']
        
        # Get course details
        course = Course.find_by_id(course_id)
        if not course:
            return jsonify({'message': 'Course not found'}), 404
        
        # Get user details
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get instructor details
        instructor = User.find_by_id(course.get('instructor'))
        instructor_name = instructor.get('fullName', 'Instructor') if instructor else 'Instructor'
        
        # Generate certificate
        cert_id, message = Certificate.generate_for_user(
            user_id=user_id,
            course_id=course_id,
            course_title=course.get('title', 'Course'),
            user_name=user.get('fullName', 'Student'),
            instructor_name=instructor_name
        )
        
        if not cert_id:
            return jsonify({'message': message}), 400
        
        # Get the generated certificate
        certificate = Certificate.find_by_id(cert_id)
        
        return jsonify({
            '_id': cert_id,
            'certificate': to_str_id(certificate),
            'message': message
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error generating certificate: {str(e)}'}), 500

@certificates.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_certificates(user_id):
    """Get all certificates for a user"""
    try:
        current_user = get_jwt_identity()
        
        # Users can only view their own certificates
        if current_user != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        certificates_list = Certificate.find_by_user(user_id)
        return jsonify(serialize_list(certificates_list)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching certificates: {str(e)}'}), 500

@certificates.route('/<cert_id>', methods=['GET'])
def get_certificate(cert_id):
    """Get a specific certificate by ID"""
    try:
        certificate = Certificate.find_by_id(cert_id)
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        return jsonify(to_str_id(certificate)), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching certificate: {str(e)}'}), 500

@certificates.route('/verify', methods=['POST'])
def verify_certificate():
    """Verify certificate authenticity"""
    try:
        data = request.get_json() or {}
        
        certificate_id = data.get('certificateId')
        verification_code = data.get('verificationCode')
        
        if not certificate_id and not verification_code:
            return jsonify({'message': 'Certificate ID or verification code is required'}), 400
        
        valid, result = Certificate.verify_certificate(
            certificate_id=certificate_id,
            verification_code=verification_code
        )
        
        if valid:
            return jsonify(result), 200
        else:
            return jsonify({'valid': False, 'message': result}), 404
            
    except Exception as e:
        return jsonify({'message': f'Error verifying certificate: {str(e)}'}), 500

@certificates.route('/check-eligibility/<course_id>', methods=['GET'])
@jwt_required()
def check_eligibility(course_id):
    """Check if user is eligible for certificate"""
    try:
        user_id = get_jwt_identity()
        
        eligible, message = Certificate.check_eligibility(user_id, course_id)
        
        return jsonify({
            'eligible': eligible,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error checking eligibility: {str(e)}'}), 500

@certificates.route('/<cert_id>/pdf', methods=['GET'])
@jwt_required()
def download_certificate_pdf(cert_id):
    """Download certificate as PDF"""
    try:
        user_id = get_jwt_identity()
        
        # Get certificate
        certificate = Certificate.find_by_id(cert_id)
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verify user owns this certificate
        if certificate.get('userId') != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate)
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"certificate_{certificate.get('certificateId')}.pdf"
        )
        
    except Exception as e:
        return jsonify({'message': f'Error downloading certificate: {str(e)}'}), 500

def generate_certificate_pdf(certificate):
    """Generate PDF certificate using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF with landscape orientation
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        # Draw border
        c.setStrokeColor(colors.HexColor('#4a6bdf'))
        c.setLineWidth(3)
        c.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch)
        
        # Draw inner border
        c.setLineWidth(1)
        c.rect(0.6*inch, 0.6*inch, width-1.2*inch, height-1.2*inch)
        
        # Title
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.HexColor('#4a6bdf'))
        c.drawCentredString(width/2, height-1.5*inch, "CERTIFICATE OF COMPLETION")
        
        # Subtitle
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height-2*inch, "This is to certify that")
        
        # Student name
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(width/2, height-2.7*inch, certificate.get('userName', 'Student'))
        
        # Course completion text
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height-3.3*inch, "has successfully completed the course")
        
        # Course title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor('#4a6bdf'))
        c.drawCentredString(width/2, height-3.9*inch, certificate.get('courseTitle', 'Course'))
        
        # Date
        issue_date = certificate.get('issueDate')
        if isinstance(issue_date, datetime):
            date_str = issue_date.strftime('%B %d, %Y')
        else:
            date_str = datetime.utcnow().strftime('%B %d, %Y')
        
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height-4.5*inch, f"Issued on {date_str}")
        
        # Instructor signature line
        c.setFont("Helvetica", 11)
        c.line(1.5*inch, 1.5*inch, 3.5*inch, 1.5*inch)
        c.drawCentredString(2.5*inch, 1.2*inch, certificate.get('instructorName', 'Instructor'))
        c.drawCentredString(2.5*inch, 1*inch, "Instructor")
        
        # Certificate ID
        c.drawCentredString(width-2.5*inch, 1.2*inch, f"Certificate ID: {certificate.get('certificateId', 'N/A')}")
        c.drawCentredString(width-2.5*inch, 1*inch, f"Verification: {certificate.get('verificationCode', 'N/A')}")
        
        # Seal/Logo placeholder
        c.setFillColor(colors.HexColor('#4a6bdf'))
        c.circle(width-2.5*inch, height-1.5*inch, 0.5*inch, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width-2.5*inch, height-1.5*inch, "EDULearn")
        
        # Save PDF
        c.save()
        
        # Reset buffer position
        buffer.seek(0)
        return buffer
        
    except ImportError:
        # If reportlab is not installed, return a simple text-based PDF
        return generate_simple_pdf(certificate)

def generate_simple_pdf(certificate):
    """Generate a simple PDF if reportlab is not available"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-100, "CERTIFICATE OF COMPLETION")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-200, certificate.get('userName', 'Student'))
    c.drawCentredString(width/2, height-250, certificate.get('courseTitle', 'Course'))
    c.drawCentredString(width/2, height-300, f"Certificate ID: {certificate.get('certificateId', 'N/A')}")
    
    c.save()
    buffer.seek(0)
    return buffer

@certificates.route('/all', methods=['GET'])
@jwt_required()
def get_all_certificates():
    """Get all certificates (admin only)"""
    try:
        certificates_list = Certificate.find_all()
        return jsonify(serialize_list(certificates_list)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching certificates: {str(e)}'}), 500
