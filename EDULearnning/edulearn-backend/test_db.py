from flask import Flask
from config import Config
from extensions import mongo

app = Flask(__name__)
app.config.from_object(Config)
mongo.init_app(app)

with app.app_context():
    try:
        # Try to access db
        mongo.db.command('ping')
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
