import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vocabulary_test_system_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../vocabulary.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key'
    DEBUG = True