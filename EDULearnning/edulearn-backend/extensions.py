from flask_pymongo import PyMongo

# Single shared Mongo client for the whole app
mongo = PyMongo()
