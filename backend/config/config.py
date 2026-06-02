import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vocabulary_test_system_secret_key_that_is_long_enough_for_security'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../vocabulary.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super_secret_jwt_key_that_is_at_least_32_bytes_long_for_sha256'
    LLM_API_KEY = os.environ.get('LLM_API_KEY') or os.environ.get('OPENAI_API_KEY') or ''
    LLM_API_BASE = os.environ.get('LLM_API_BASE') or 'https://api.openai.com/v1'
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'gpt-4o-mini'
    DEBUG = True
