import os

class Config:
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://vishwakarmaadarsh9606_db_user:24QJ7RQFIOn2FypN@adarsh.q0b4unn.mongodb.net/edulearn?retryWrites=true&w=majority&appName=adarsh'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_super_secret_key'
