import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'twitter-analiz-secret-key-2024'
    BASEDIR = BASE_DIR
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    TWEET_ARSIVLERI_FOLDER = BASE_DIR / 'tweet_arsivleri'
    SONUCLAR_FOLDER = BASE_DIR / 'sonuclar'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Analysis settings
    DEFAULT_LDA_TOPICS = 8
    DEFAULT_BATCH_SIZE = 16
    
    # Create directories if they don't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    SONUCLAR_FOLDER.mkdir(exist_ok=True)
    (SONUCLAR_FOLDER / 'lda_sonuclari').mkdir(exist_ok=True)
    (SONUCLAR_FOLDER / 'duygu_sonuclari').mkdir(exist_ok=True)
    (SONUCLAR_FOLDER / 'wordcloud_sonuclari').mkdir(exist_ok=True)
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URI = f'sqlite:///{BASE_DIR}/dev.db'
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/prod.db'
    
class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
} 