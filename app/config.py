import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key-catalogue-2026'
    
    # Handle PostgreSQL URL scheme (SQLAlchemy 2.0 requires postgresql:// instead of postgres://)
    db_url = os.environ.get('DATABASE_URL') or f"sqlite:///{basedir / 'catalogue.db'}"
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads configuration
    UPLOAD_FOLDER = basedir / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}
    
    # Cloudinary configuration (optional persistent image storage)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Security & session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
