import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vocabulary_test_system_secret_key_that_is_long_enough_for_security'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../vocabulary.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super_secret_jwt_key_that_is_at_least_32_bytes_long_for_sha256'
    DEBUG = True