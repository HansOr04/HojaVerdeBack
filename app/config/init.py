import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(file))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))
class Config:
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds
