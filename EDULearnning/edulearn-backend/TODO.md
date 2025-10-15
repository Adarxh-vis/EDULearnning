# Backend Refactor & Completion TODO

Scope: Stabilize Flask backend, fix imports, centralize Mongo connection, add missing endpoints, ensure JSON serialization, enable CORS, and provide run instructions.

- [x] Create shared Mongo extension (extensions.py)
- [x] Add package init files: routes/, modles/, middleware/, utils/
- [x] Add utils/serializers.py for ObjectId-safe JSON serialization
- [x] Update models to use shared mongo (modles/user.py, modles/course.py)
- [x] Fix middleware import (middleware/auth_middleware.py)
- [x] Fix routes/auth.py: correct imports, add teacher signup, consistent responses
- [x] Fix routes/users.py: correct imports, use mongo/ObjectId, JSON-safe responses, validate updates
- [x] Fix routes/courses.py: correct imports, add GET list, GET by id, filter /my by instructor id
- [x] Update app.py: initialize extensions.mongo with app, add CORS, register blueprints with url_prefix (/api/*), add JSON error handlers
- [x] Add requirements.txt with dependencies
- [ ] Run and verify endpoints with curl/Postman
- [ ] Document Windows run instructions in README

Progress notes:
- 2025-09-25: Created extensions.py with shared PyMongo instance.
- 2025-09-25: Completed refactor, added endpoints, CORS, and requirements.
