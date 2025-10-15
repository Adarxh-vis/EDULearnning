EDULearn Backend (Flask + MongoDB)

Overview
A Flask REST API with:
- MongoDB via Flask-PyMongo
- JWT auth via Flask-JWT-Extended
- CORS enabled for the frontend
- Clean package structure and shared Mongo connection
- JSON-safe serialization for Mongo ObjectIds

API Base URL
http://localhost:5000/api

Key Endpoints
- Auth
  - POST /auth/student/signup
  - POST /auth/teacher/signup
  - POST /auth/login
- Users
  - GET /users/me            (JWT)
  - PUT /users/me            (JWT)
- Courses
  - GET /courses
  - GET /courses/:id
  - GET /courses/my          (JWT)
  - POST /courses            (JWT)

Project Structure
edulearn-backend/
  app.py
  config.py
  extensions.py         # shared mongo = PyMongo()
  requirements.txt
  routes/
    __init__.py
    auth.py
    users.py
    courses.py
  modles/               # keep 'modles' name to match existing imports
    __init__.py
    user.py
    course.py
  middleware/
    __init__.py
    auth_middleware.py
  utils/
    __init__.py
    serializers.py
  TODO.md

Prerequisites
- Python 3.10+
- MongoDB running locally, or a cloud MongoDB URI
- Windows 11 (instructions below use cmd.exe)

Environment Variables
- MONGO_URI: defaults to mongodb://localhost:27017/edulearn
- JWT_SECRET_KEY: defaults to your_super_secret_key

Option A: Quick Run (python app.py)
1) Open a terminal in the repository root:
   cd edulearn-backend

2) Create and activate a virtual environment:
   py -3 -m venv .venv
   .venv\Scripts\activate

3) Install dependencies:
   pip install -r requirements.txt

4) Set environment variables (adjust as needed):
   set MONGO_URI=mongodb://localhost:27017/edulearn
   set JWT_SECRET_KEY=your_super_secret_key

5) Run the server:
   python app.py

6) API will be available at:
   http://localhost:5000/api

Option B: Using Flask CLI
1) From edulearn-backend directory (after steps 1-4 above):
   set FLASK_APP=app.py
   set FLASK_ENV=development
   flask run

Smoke Test with curl
- Signup (Student):
  curl -X POST http://localhost:5000/api/auth/student/signup ^
    -H "Content-Type: application/json" ^
    -d "{\"fullName\":\"Alice\",\"email\":\"alice@example.com\",\"password\":\"Passw0rd!\"}"

- Login:
  curl -X POST http://localhost:5000/api/auth/login ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"alice@example.com\",\"password\":\"Passw0rd!\"}"

  Response will include: {"token":"<JWT>", "user":{...}}

- Get Current User (replace <TOKEN> with JWT):
  curl http://localhost:5000/api/users/me ^
    -H "Authorization: Bearer <TOKEN>"

- Create Course (JWT reqd):
  curl -X POST http://localhost:5000/api/courses ^
    -H "Authorization: Bearer <TOKEN>" ^
    -H "Content-Type: application/json" ^
    -d "{\"title\":\"Flask 101\",\"description\":\"Intro course\",\"category\":\"Programming\",\"price\":0}"

- List Courses:
  curl http://localhost:5000/api/courses

- Get My Courses (JWT reqd):
  curl http://localhost:5000/api/courses/my ^
    -H "Authorization: Bearer <TOKEN>"

Frontend Integration
The provided js/api.js expects API at http://localhost:5000/api and paths:
- /auth/student/signup, /auth/teacher/signup, /auth/login
- /courses, /courses/:id, /courses/my
- /users/me

Notes
- If running Mongo on a non-default URI or remote cluster, set MONGO_URI accordingly.
- For production, use a strong JWT_SECRET_KEY and disable debug.
- To add admin-only routes, use middleware/auth_middleware.py: @admin_required.

Troubleshooting
- Module import errors: ensure you run commands from the edulearn-backend directory so Python package imports work (routes, modles, utils are packages with __init__.py).
- Mongo connection issues: verify MongoDB is running and your MONGO_URI is correct.
- CORS/browser issues: CORS is enabled for /api/*; verify requests target http://localhost:5000/api.
