#!/usr/bin/env python3
"""
Twitter Analiz Platformu - Ana Çalıştırma Dosyası
=================================================

Bu dosya Flask uygulamasını başlatır.
"""

import os
import sys
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from app import create_app
from config import config

def main():
    """Ana fonksiyon - Flask uygulamasını başlatır"""
    
    # Konfigürasyon ortamını belirle
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    print(f"🚀 Twitter Analiz Platformu başlatılıyor...")
    print(f"📁 Proje dizini: {project_root}")
    print(f"⚙️  Konfigürasyon: {config_name}")
    
    # Flask uygulamasını oluştur
    app = create_app(config_name)
    
    # Geliştirme ortamında debug bilgilerini göster
    if config_name == 'development':
        print("\n📋 Mevcut Route'lar:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                print(f"   {rule.endpoint:30} {methods:10} {rule.rule}")
        
        print(f"\n🔗 Uygulama URL'leri:")
        print(f"   Ana Sayfa: http://localhost:5000")
        print(f"   Veri Seçimi: http://localhost:5000/veri-secimi")
        print(f"   API Sağlık: http://localhost:5000/api/health")
        print(f"   API Dosyalar: http://localhost:5000/api/files")
    
    # Dosya yapısını kontrol et
    check_directory_structure()
    
    # Uygulamayı başlat
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=(config_name == 'development'),
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Uygulama kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Uygulama başlatma hatası: {e}")
        sys.exit(1)

def check_directory_structure():
    """Gerekli klasörlerin varlığını kontrol eder ve eksik olanları oluşturur"""
    
    required_dirs = [
        'tweet_arsivleri',
        'sonuclar',
        'sonuclar/lda_sonuclari',
        'sonuclar/duygu_sonuclari', 
        'sonuclar/wordcloud_sonuclari',
        'uploads',
        'static/css',
        'static/js',
        'static/images'
    ]
    
    print("\n📂 Klasör yapısı kontrol ediliyor...")
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Oluşturuldu: {dir_path}")
        else:
            print(f"   ✓ Mevcut: {dir_path}")
    
    # Tweet arşivleri klasörünü kontrol et
    tweet_arsivleri = project_root / 'tweet_arsivleri'
    json_files = list(tweet_arsivleri.glob('*.json'))
    
    if json_files:
        print(f"\n📄 Tweet arşivleri bulundu: {len(json_files)} dosya")
        for file in json_files[:3]:  # İlk 3 dosyayı göster
            file_size = file.stat().st_size
            print(f"   - {file.name} ({format_file_size(file_size)})")
        if len(json_files) > 3:
            print(f"   ... ve {len(json_files) - 3} dosya daha")
    else:
        print(f"\n⚠️  Tweet arşivi dosyası bulunamadı!")
        print(f"   JSON formatındaki tweet dosyalarınızı '{tweet_arsivleri}' klasörüne koyun.")

def format_file_size(bytes_size):
    """Dosya boyutunu insan okunabilir formata çevirir"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

if __name__ == '__main__':
    main() 