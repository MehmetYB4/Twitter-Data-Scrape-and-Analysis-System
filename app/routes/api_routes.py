"""
API Route'ları
==============

RESTful API endpoint'leri.
"""

from flask import Blueprint, jsonify, request, current_app
from pathlib import Path
import json
import os
from datetime import datetime
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Sistem sağlık kontrolü"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/files', methods=['GET'])
def get_files():
    """Dosya listesini döndürür"""
    try:
        arsiv_klasoru = Path('tweet_arsivleri')
        if not arsiv_klasoru.exists():
            arsiv_klasoru.mkdir(exist_ok=True)
            return jsonify({
                'success': True,
                'data': []
            })
        
        files = []
        for dosya_yolu in arsiv_klasoru.glob('*.json'):
            try:
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                tweet_sayisi = len(data) if isinstance(data, list) else 0
                dosya_boyutu = dosya_yolu.stat().st_size
                
                # Dosya ID'si olarak dosya adını kullan
                file_id = dosya_yolu.name
                
                files.append({
                    'id': file_id,
                    'dosya_adi': dosya_yolu.name,
                    'dosya_yolu': str(dosya_yolu),
                    'tweet_sayisi': tweet_sayisi,
                    'dosya_boyutu': dosya_boyutu,
                    'olusturma_tarihi': datetime.fromtimestamp(dosya_yolu.stat().st_ctime).isoformat(),
                    'son_degisiklik': datetime.fromtimestamp(dosya_yolu.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"Dosya okuma hatası {dosya_yolu}: {e}")
                # Hatalı dosya için de temel bilgi ekle
                files.append({
                    'id': dosya_yolu.name,
                    'dosya_adi': dosya_yolu.name,
                    'dosya_yolu': str(dosya_yolu),
                    'tweet_sayisi': 0,
                    'dosya_boyutu': dosya_yolu.stat().st_size if dosya_yolu.exists() else 0,
                    'olusturma_tarihi': datetime.fromtimestamp(dosya_yolu.stat().st_ctime).isoformat() if dosya_yolu.exists() else datetime.now().isoformat(),
                    'son_degisiklik': datetime.fromtimestamp(dosya_yolu.stat().st_mtime).isoformat() if dosya_yolu.exists() else datetime.now().isoformat(),
                    'hata': str(e)
                })
                continue
        
        return jsonify({
            'success': True,
            'data': files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/files/stats', methods=['GET'])
def get_file_stats():
    """Dosya istatistiklerini döndürür"""
    try:
        arsiv_klasoru = Path('tweet_arsivleri')
        if not arsiv_klasoru.exists():
            return jsonify({
                'success': True,
                'data': {
                    'total_files': 0,
                    'total_tweets': 0,
                    'total_size_mb': 0,
                    'tweets_today': 0,
                    'largest_file': None,
                    'newest_file': None
                }
            })
        
        total_files = 0
        total_tweets = 0
        total_size = 0
        tweets_today = 0
        largest_file = {'name': '', 'size': 0}
        newest_file = {'name': '', 'date': None}
        
        today = datetime.now().date()
        
        for dosya_yolu in arsiv_klasoru.glob('*.json'):
            try:
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                tweet_count = len(data) if isinstance(data, list) else 0
                file_size = dosya_yolu.stat().st_size
                file_date = datetime.fromtimestamp(dosya_yolu.stat().st_ctime)
                
                total_files += 1
                total_tweets += tweet_count
                total_size += file_size
                
                # Bugün oluşturulan tweet'ler
                if file_date.date() == today:
                    tweets_today += tweet_count
                
                # En büyük dosya
                if file_size > largest_file['size']:
                    largest_file = {
                        'name': dosya_yolu.name,
                        'size': file_size,
                        'tweets': tweet_count
                    }
                
                # En yeni dosya
                if newest_file['date'] is None or file_date > newest_file['date']:
                    newest_file = {
                        'name': dosya_yolu.name,
                        'date': file_date,
                        'tweets': tweet_count
                    }
                    
            except Exception as e:
                print(f"Dosya okuma hatası {dosya_yolu}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': {
                'total_files': total_files,
                'total_tweets': total_tweets,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'tweets_today': tweets_today,
                'largest_file': largest_file if largest_file['name'] else None,
                'newest_file': {
                    'name': newest_file['name'],
                    'date': newest_file['date'].isoformat() if newest_file['date'] else None,
                    'tweets': newest_file.get('tweets', 0)
                } if newest_file['name'] else None,
                'avg_tweets_per_file': round(total_tweets / total_files, 1) if total_files > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/files/<file_id>', methods=['GET'])
def get_file_details(file_id):
    """Belirli bir dosyanın detaylarını döndürür"""
    try:
        # Dosya ID'si ile dosya bulma (basit implementasyon)
        arsiv_klasoru = Path('tweet_arsivleri')
        
        for dosya_yolu in arsiv_klasoru.glob('*.json'):
            if dosya_yolu.name == file_id or dosya_yolu.stem == file_id:
                try:
                    with open(dosya_yolu, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # İlk 5 tweet'i örnek olarak al
                    sample_tweets = data[:5] if isinstance(data, list) and len(data) > 0 else []
                    
                    # Kelime istatistikleri
                    all_text = ' '.join(data) if isinstance(data, list) else ''
                    word_count = len(all_text.split())
                    unique_words = len(set(all_text.lower().split()))
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'id': file_id,
                            'dosya_adi': dosya_yolu.name,
                            'tweet_sayisi': len(data) if isinstance(data, list) else 0,
                            'dosya_boyutu': dosya_yolu.stat().st_size,
                            'word_count': word_count,
                            'unique_words': unique_words,
                            'sample_tweets': sample_tweets,
                            'olusturma_tarihi': datetime.fromtimestamp(dosya_yolu.stat().st_ctime).isoformat(),
                            'son_degisiklik': datetime.fromtimestamp(dosya_yolu.stat().st_mtime).isoformat()
                        }
                    })
                    
                except Exception as e:
                    continue
        
        return jsonify({
            'success': False,
            'error': 'Dosya bulunamadı'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/files/<file_id>/preview', methods=['GET'])
def get_file_preview(file_id):
    """Dosya önizlemesi döndürür"""
    try:
        arsiv_klasoru = Path('tweet_arsivleri')
        
        for dosya_yolu in arsiv_klasoru.glob('*.json'):
            if dosya_yolu.name == file_id or dosya_yolu.stem == file_id:
                try:
                    with open(dosya_yolu, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # İlk 10 tweet'i önizleme için al
                    preview_tweets = data[:10] if isinstance(data, list) and len(data) > 0 else []
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'filename': dosya_yolu.name,
                            'total_tweets': len(data) if isinstance(data, list) else 0,
                            'preview': preview_tweets
                        }
                    })
                    
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Dosya okuma hatası: {str(e)}'
                    }), 500
        
        return jsonify({
            'success': False,
            'error': 'Dosya bulunamadı'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/system/stats', methods=['GET'])
def get_system_stats():
    """Sistem istatistiklerini döndürür"""
    try:
        import psutil
        import platform
        
        # CPU ve bellek kullanımı
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'success': True,
            'data': {
                'cpu_usage': cpu_percent,
                'memory_usage': {
                    'percent': memory.percent,
                    'used_mb': round(memory.used / (1024 * 1024), 1),
                    'total_mb': round(memory.total / (1024 * 1024), 1)
                },
                'disk_usage': {
                    'percent': round((disk.used / disk.total) * 100, 1),
                    'used_gb': round(disk.used / (1024 * 1024 * 1024), 1),
                    'total_gb': round(disk.total / (1024 * 1024 * 1024), 1)
                },
                'platform': {
                    'system': platform.system(),
                    'version': platform.version(),
                    'python_version': platform.python_version()
                },
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except ImportError:
        # psutil yoksa mock data döndür
        return jsonify({
            'success': True,
            'data': {
                'cpu_usage': 15.2,
                'memory_usage': {
                    'percent': 45.8,
                    'used_mb': 234.5,
                    'total_mb': 512.0
                },
                'disk_usage': {
                    'percent': 12.3,
                    'used_gb': 1.2,
                    'total_gb': 10.0
                },
                'platform': {
                    'system': 'Windows',
                    'version': '10',
                    'python_version': '3.9.0'
                },
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """Dosya yükleme endpoint'i"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Dosya seçilmedi'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Dosya adı boş'
            }), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({
                'success': False,
                'error': 'Sadece JSON dosyaları desteklenir'
            }), 400
        
        # Dosyayı kaydet
        arsiv_klasoru = Path('tweet_arsivleri')
        arsiv_klasoru.mkdir(exist_ok=True)
        
        dosya_yolu = arsiv_klasoru / file.filename
        file.save(dosya_yolu)
        
        # Dosya içeriğini kontrol et
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tweet_sayisi = len(data) if isinstance(data, list) else 0
        except:
            dosya_yolu.unlink()  # Hatalı dosyayı sil
            return jsonify({
                'success': False,
                'error': 'Geçersiz JSON formatı'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'dosya_adi': file.filename,
                'tweet_sayisi': tweet_sayisi,
                'dosya_boyutu': dosya_yolu.stat().st_size,
                'mesaj': 'Dosya başarıyla yüklendi'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Dosya silme endpoint'i"""
    try:
        arsiv_klasoru = Path('tweet_arsivleri')
        dosya_yolu = arsiv_klasoru / filename
        
        if not dosya_yolu.exists():
            return jsonify({
                'success': False,
                'error': 'Dosya bulunamadı'
            }), 404
        
        dosya_yolu.unlink()
        
        return jsonify({
            'success': True,
            'data': {
                'mesaj': f'{filename} başarıyla silindi'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Analiz özet istatistikleri"""
    try:
        # Bu endpoint analiz sonuçlarının özetini döndürür
        # Şimdilik mock data, gerçek implementasyon analiz sonuçlarını okuyacak
        
        return jsonify({
            'success': True,
            'data': {
                'total_analyses': 1,
                'completed_analyses': 1,
                'failed_analyses': 0,
                'avg_processing_time': 15.2,
                'most_common_topics': [
                    {'topic': 'Sosyal Medya', 'frequency': 32},
                    {'topic': 'Teknoloji', 'frequency': 28},
                    {'topic': 'Eğitim', 'frequency': 25}
                ],
                'sentiment_distribution': {
                    'positive': 65,
                    'negative': 20,
                    'neutral': 15
                },
                'last_analysis': {
                    'date': datetime.now().isoformat(),
                    'tweet_count': 20,
                    'duration': 15.2
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 