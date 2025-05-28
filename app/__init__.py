"""
Twitter Analiz Web Uygulaması
=============================

Flask tabanlı web arayüzü ile Twitter analiz işlemlerini yöneten uygulama.
"""

from flask import Flask
from config import config
import os


def create_app(config_name=None):
    """Application factory pattern ile Flask uygulaması oluşturur"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Static ve template klasörlerini doğru yollar ile oluştur
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='templates')
    app.config.from_object(config[config_name])
    
    # Blueprint'leri kaydet
    from .routes.main_routes import main_bp
    from .routes.api_routes import api_bp
    from .routes.analiz_routes import analiz_bp
    from .routes.twitter_routes import twitter_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(analiz_bp, url_prefix='/analiz')
    app.register_blueprint(twitter_bp)
    
    return app 