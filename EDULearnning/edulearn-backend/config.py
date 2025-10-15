import os

class Config:
    MONGO_URI = os.environ.get('MONGO_URI') or '//mongodb url'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_super_secret_key'

