import os
from datetime import timedelta
import sqlalchemy

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PERMANENT_SESSION = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=10)
    
    UPLOAD_AVATARS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'avatars')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    
    
class DevConfig(Config):
    UPLOAD_AVATARS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'avatars')
    DEBUG = True
    
class ProdConfig(Config):
    UPLOAD_AVATARS_FOLDER = '../www/var/avatars'
    DEBUG = False
        