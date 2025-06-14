"""
Ana Sayfa Route'ları
===================

Web uygulamasının ana sayfalarını yöneten route'lar.
"""

from flask import Blueprint, render_template, current_app
import os
import json
from pathlib import Path
from app.utils.language import get_text

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ana sayfa - Dashboard"""
    return render_template('index.html', 
                         title=get_text('pages.dashboard.title'),
                         page='dashboard')

@main_bp.route('/veri-secimi')
def veri_secimi():
    """Veri seçimi sayfası"""
    # Tweet arşivi dosyalarını listele
    tweet_arsivleri_path = current_app.config['TWEET_ARSIVLERI_FOLDER']
    dosyalar = []
    
    if tweet_arsivleri_path.exists():
        for dosya in tweet_arsivleri_path.glob('*.json'):
            try:
                # Dosya bilgilerini al
                dosya_boyutu = dosya.stat().st_size
                dosya_tarihi = dosya.stat().st_mtime
                
                # JSON dosyasının içeriğini kontrol et
                with open(dosya, 'r', encoding='utf-8') as f:
                    veri = json.load(f)
                    tweet_sayisi = len(veri) if isinstance(veri, list) else 0
                
                dosyalar.append({
                    'isim': dosya.name,
                    'yol': str(dosya),
                    'boyut': dosya_boyutu,
                    'tarih': dosya_tarihi,
                    'tweet_sayisi': tweet_sayisi
                })
            except Exception as e:
                print(f"Dosya okuma hatası {dosya.name}: {e}")
    
    return render_template('veri_secimi.html', 
                         title=get_text('pages.data_selection.title'),
                         page='veri-secimi',
                         dosyalar=dosyalar)

@main_bp.route('/analiz-konfigurasyonu')
def analiz_konfigurasyonu():
    """Analiz konfigürasyon sayfası"""
    return render_template('analiz_konfigurasyonu.html',
                         title=get_text('pages.analysis_configuration.title'),
                         page='analiz-konfigurasyonu')

@main_bp.route('/sonuclar')
def sonuclar():
    """Sonuçlar sayfası"""
    return render_template('sonuclar.html',
                         title=get_text('pages.results.title'),
                         page='sonuclar')

@main_bp.route('/test-sonuclar')
def test_sonuclar():
    """Test sonuçlar sayfası"""
    return render_template('test_sonuclar.html',
                         title=get_text('pages.results.title'),
                         page='test-sonuclar')

@main_bp.route('/sonuclar/<analiz_id>')
def sonuc_detay(analiz_id):
    """Belirli bir analizin detay sayfası"""
    return render_template('sonuc_detay.html',
                         title=f'{get_text("pages.results.title")} - {analiz_id}',
                         page='sonuc-detay',
                         analiz_id=analiz_id) 