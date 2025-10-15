from flask import Flask, jsonify, send_from_directory
import os
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from extensions import mongo

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize shared Mongo and JWT
    mongo.init_app(app)
    JWTManager(app)

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Import and register blueprints with URL prefixes
    from routes.auth import auth as auth_bp
    from routes.users import users as users_bp
    from routes.courses_fixed import courses as courses_bp
    from routes.assessments import assessments as assessments_bp
    from routes.test_results import test_results as test_results_bp
    from routes.certificates import certificates as certificates_bp
    from routes.admin import admin as admin_bp
    from routes.messages import messages as messages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(assessments_bp, url_prefix="/api/assessments")
    app.register_blueprint(test_results_bp, url_prefix="/api/test-results")
    app.register_blueprint(certificates_bp, url_prefix="/api/certificates")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")

    # Serve frontend
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @app.route('/')
    def serve_homepage():
        return send_from_directory(FRONTEND_DIR, 'homepage.html')

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

    # Serve any existing file under project root (html, css, images, etc.)
    @app.route('/<path:filename>')
    def serve_static_any(filename):
        target = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(target):
            directory = os.path.dirname(filename)
            basename = os.path.basename(filename)
            base_dir = os.path.join(FRONTEND_DIR, directory) if directory else FRONTEND_DIR
            return send_from_directory(base_dir, basename)
        return jsonify({"message": "Not found"}), 404

    # Short routes
    @app.route('/login')
    def route_login():
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.route('/signup')
    def route_signup():
        return send_from_directory(FRONTEND_DIR, 'studentSignUp.html')

    @app.route('/teacher/login')
    def route_teacher_login():
        return send_from_directory(FRONTEND_DIR, 'teacherlogin.html')

    @app.route('/teacher/signup')
    def route_teacher_signup():
        return send_from_directory(FRONTEND_DIR, 'teacherSignUp.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"message": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"message": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
