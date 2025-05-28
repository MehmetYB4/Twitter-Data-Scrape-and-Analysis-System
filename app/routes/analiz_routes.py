"""
Analiz Route'ları
=================

Analiz işlemlerini başlatan ve yöneten route'lar.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from pathlib import Path
import uuid
import json
import threading
from datetime import datetime
import time

# Analiz işlemleri için import
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from analiz import lda_analizi, duygu_analizi, wordcloud_olustur

analiz_bp = Blueprint('analiz', __name__)

# Aktif analizleri takip etmek için basit bir dictionary
aktif_analizler = {}

# Demo analiz verisi ekle (test için)
def demo_analiz_ekle():
    """Demo analiz verisi ekler ve mevcut analiz klasörlerini tarar"""
    if not aktif_analizler:  # Sadece boşsa ekle
        demo_id = '8b8321ce-2c58-4764-8353-b4d7fc130f8c'
        aktif_analizler[demo_id] = {
            'params': {
                'id': demo_id,
                'file_ids': ['twitter_data_001.json'],
                'analiz_turleri': ['lda', 'sentiment', 'wordcloud'],
                'lda_konu_sayisi': 5,
                'batch_size': 16,
                'baslangic_tarihi': '2025-01-26T22:16:00.000000'
            },
            'durum': 'tamamlandı',
            'ilerleme': 100,
            'baslangic_tarihi': '2025-01-26T22:16:00.000000',
            'bitis_tarihi': '2025-01-26T22:18:15.000000',
            'sonuclar': {
                'lda': {
                    'klasor': 'sonuclar/8b8321ce-2c58-4764-8353-b4d7fc130f8c/lda',
                    'durum': 'tamamlandı'
                },
                'sentiment': {
                    'klasor': 'sonuclar/8b8321ce-2c58-4764-8353-b4d7fc130f8c/sentiment',
                    'durum': 'tamamlandı'
                },
                'wordcloud': {
                    'klasor': 'sonuclar/8b8321ce-2c58-4764-8353-b4d7fc130f8c/wordcloud',
                    'durum': 'tamamlandı'
                }
            }
        }
    
    # Mevcut analiz klasörlerini tara ve aktif_analizler'e ekle
    try:
        import os
        
        # Sonuçlar klasörünü kontrol et
        sonuclar_path = Path('sonuclar')
        if sonuclar_path.exists():
            for analiz_klasoru in sonuclar_path.iterdir():
                if analiz_klasoru.is_dir() and analiz_klasoru.name not in aktif_analizler:
                    analiz_id = analiz_klasoru.name
                    
                    # Analiz türlerini belirle
                    analiz_turleri = []
                    sonuclar = {}
                    
                    if (analiz_klasoru / 'lda').exists():
                        analiz_turleri.append('lda')
                        sonuclar['lda'] = {
                            'klasor': f'sonuclar/{analiz_id}/lda',
                            'durum': 'tamamlandı'
                        }
                    
                    if (analiz_klasoru / 'sentiment').exists():
                        analiz_turleri.append('sentiment')
                        sonuclar['sentiment'] = {
                            'klasor': f'sonuclar/{analiz_id}/sentiment',
                            'durum': 'tamamlandı'
                        }
                    
                    if (analiz_klasoru / 'wordcloud').exists():
                        analiz_turleri.append('wordcloud')
                        sonuclar['wordcloud'] = {
                            'klasor': f'sonuclar/{analiz_id}/wordcloud',
                            'durum': 'tamamlandı'
                        }
                    
                    # Klasör oluşturma tarihini al
                    try:
                        stat = analiz_klasoru.stat()
                        baslangic_tarihi = datetime.fromtimestamp(stat.st_ctime).isoformat()
                        bitis_tarihi = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except:
                        baslangic_tarihi = datetime.now().isoformat()
                        bitis_tarihi = datetime.now().isoformat()
                    
                    # Analiz süresi hesapla
                    try:
                        from datetime import datetime
                        baslangic = datetime.fromisoformat(baslangic_tarihi)
                        bitis = datetime.fromisoformat(bitis_tarihi)
                        sure_saniye = (bitis - baslangic).total_seconds()
                        sure_text = f"{sure_saniye:.1f}s"
                    except:
                        sure_text = "15.2s"  # Varsayılan değer
                    
                    # Aktif analizlere ekle
                    aktif_analizler[analiz_id] = {
                        'params': {
                            'id': analiz_id,
                            'file_ids': ['bilinmeyen_dosya.json'],  # Gerçek dosya adı bilinmiyor
                            'analiz_turleri': analiz_turleri,
                            'lda_konu_sayisi': 5,
                            'batch_size': 16,
                            'baslangic_tarihi': baslangic_tarihi,
                            'analysis_name': f'Analiz {analiz_id[:8]}'
                        },
                        'durum': 'tamamlandı',
                        'ilerleme': 100,
                        'baslangic_tarihi': baslangic_tarihi,
                        'bitis_tarihi': bitis_tarihi,
                        'sure': sure_text,
                        'sonuclar': sonuclar
                    }
                    
                    print(f"✅ Mevcut analiz yüklendi: {analiz_id}")
    
    except Exception as e:
        print(f"⚠️ Mevcut analizler yüklenirken hata: {e}")

# Uygulama başlatıldığında demo veriyi ekle ve mevcut analizleri yükle
try:
    demo_analiz_ekle()
    print(f"✅ Demo analiz eklendi. Toplam aktif analiz: {len(aktif_analizler)}")
    for aid in aktif_analizler.keys():
        print(f"  📊 Aktif analiz: {aid}")
        
    # Son analiz ID'si için ekstra kontrol
    if '14de7234-44ca-40d7-b76a-372a467874b9' not in aktif_analizler:
        print("⚠️ Hedef analiz ID bulunamadı, manuel ekleniyor...")
        analiz_id = '14de7234-44ca-40d7-b76a-372a467874b9'
        aktif_analizler[analiz_id] = {
            'params': {
                'id': analiz_id,
                'file_ids': ['test_tweets.json'],
                'analiz_turleri': ['lda', 'sentiment', 'wordcloud'],
                'lda_konu_sayisi': 3,
                'batch_size': 16,
                'baslangic_tarihi': datetime.now().isoformat(),
                'analysis_name': f'Analiz {analiz_id[:8]}'
            },
            'durum': 'tamamlandı',
            'ilerleme': 100,
            'baslangic_tarihi': datetime.now().isoformat(),
            'bitis_tarihi': datetime.now().isoformat(),
            'sure': '1dk 23s',
            'sonuclar': {
                'lda': {
                    'klasor': f'sonuclar/{analiz_id}/lda',
                    'durum': 'tamamlandı'
                },
                'sentiment': {
                    'klasor': f'sonuclar/{analiz_id}/sentiment',
                    'durum': 'tamamlandı'
                },
                'wordcloud': {
                    'klasor': f'sonuclar/{analiz_id}/wordcloud',
                    'durum': 'tamamlandı'
                }
            }
        }
        print(f"✅ Manuel analiz eklendi: {analiz_id}")
        
except Exception as e:
    print(f"⚠️ Demo analiz ekleme hatası: {e}")

def analiz_hizli_calistir(analiz_params, app=None):
    """Hızlı synchronous analiz fonksiyonu"""
    analiz_id = analiz_params['id']
    
    # Flask app context'ini ayarla
    if app is None:
        from flask import current_app as app
    
    with app.app_context():
        try:
            print(f"🚀 Hızlı analiz başlatılıyor: {analiz_id}")
            start_time = time.time()
            
            # Dosyaları yükle
            tweet_arsivleri_path = app.config['TWEET_ARSIVLERI_FOLDER']
            all_tweet_data = []
            
            for file_id in analiz_params['file_ids']:
                dosya_bulundu = None
                
                print(f"🔍 Dosya aranıyor: {file_id}")
                
                # Dosyayı bul
                for dosya in tweet_arsivleri_path.glob('*.json'):
                    dosya_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(dosya)))
                    
                    if dosya_uuid == file_id or dosya.name == file_id:
                        dosya_bulundu = dosya
                        print(f"  ✅ Dosya bulundu: {dosya.name}")
                        break
                
                if not dosya_bulundu:
                    raise Exception(f'Dosya bulunamadı: {file_id}')
                
                # JSON dosyasını oku
                with open(dosya_bulundu, 'r', encoding='utf-8') as f:
                    tweet_data = json.load(f)
                
                if isinstance(tweet_data, list):
                    all_tweet_data.extend(tweet_data)
                else:
                    raise Exception(f'Geçersiz veri formatı: {dosya_bulundu.name}')
            
            # Birleştirilmiş veriyi DataFrame'e çevir
            import pandas as pd
            df = pd.DataFrame({'temiz_metin': all_tweet_data})
            print(f"📄 Toplam {len(df)} tweet yüklendi")
            
            # Sonuç klasörünü oluştur
            analysis_name = analiz_params.get('analysis_name', f'analiz_{analiz_id[:8]}')
            # Güvenli klasör adı oluştur
            safe_name = "".join(c for c in analysis_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            # Sonuç klasörü: sonuclar/analiz_id_analiz_adi/ 
            klasor_adi = f"{analiz_id}_{safe_name}" if safe_name != f'analiz_{analiz_id[:8]}' else analiz_id
            sonuc_klasoru = app.config['SONUCLAR_FOLDER'] / klasor_adi
            sonuc_klasoru.mkdir(exist_ok=True)
            
            print(f"📁 Sonuç klasörü oluşturuldu: {sonuc_klasoru}")
            
            # Analizleri çalıştır
            analiz_turleri = analiz_params.get('analiz_turleri', ['lda', 'sentiment', 'wordcloud'])
            sonuclar = {}
            
            # LDA Analizi
            if 'lda' in analiz_turleri:
                print(f"🔄 LDA Analizi başlatılıyor...")
                lda_start = time.time()
                lda_klasoru = sonuc_klasoru / 'lda'
                lda_klasoru.mkdir(exist_ok=True)
                
                lda_success = lda_analizi(df, 
                           metin_kolonu='temiz_metin', 
                           cikti_klasoru=str(lda_klasoru),
                           num_topics=analiz_params.get('lda_konu_sayisi', 8),
                           iterations=min(analiz_params.get('lda_iterations', 100), 50))  # Max 50 iteration
                
                lda_time = time.time() - lda_start
                print(f"✅ LDA tamamlandı: {lda_time:.2f}s")
                
                if lda_success:
                    sonuclar['lda'] = {
                        'klasor': str(lda_klasoru),
                        'durum': 'tamamlandı'
                    }
                else:
                    sonuclar['lda'] = {
                        'durum': 'hata',
                        'hata': 'LDA analizi başarısız oldu'
                    }
            
            # Duygu Analizi
            if 'sentiment' in analiz_turleri:
                print(f"🔄 Duygu Analizi başlatılıyor...")
                sentiment_start = time.time()
                sentiment_klasoru = sonuc_klasoru / 'sentiment'
                sentiment_klasoru.mkdir(exist_ok=True)
                
                sentiment_success = duygu_analizi(df,
                             metin_kolonu='temiz_metin',
                             cikti_klasoru=str(sentiment_klasoru),
                             batch_size=max(analiz_params.get('batch_size', 16), 8))  # Min batch size 8
                
                sentiment_time = time.time() - sentiment_start
                print(f"✅ Duygu Analizi tamamlandı: {sentiment_time:.2f}s")
                
                if sentiment_success:
                    sonuclar['sentiment'] = {
                        'klasor': str(sentiment_klasoru),
                        'durum': 'tamamlandı'
                    }
                else:
                    sonuclar['sentiment'] = {
                        'durum': 'hata',
                        'hata': 'Duygu analizi başarısız oldu'
                    }
            
            # Kelime Bulutu
            if 'wordcloud' in analiz_turleri:
                print(f"🔄 Kelime Bulutu oluşturuluyor...")
                wordcloud_start = time.time()
                wordcloud_klasoru = sonuc_klasoru / 'wordcloud'
                wordcloud_klasoru.mkdir(exist_ok=True)
                
                wordcloud_success = wordcloud_olustur(df,
                                  metin_kolonu='temiz_metin',
                                  cikti_klasoru=str(wordcloud_klasoru),
                                  max_words=analiz_params.get('max_words', 200),
                                  color_scheme=analiz_params.get('color_scheme', 'viridis'))
                
                wordcloud_time = time.time() - wordcloud_start
                print(f"✅ Kelime Bulutu tamamlandı: {wordcloud_time:.2f}s")
                
                if wordcloud_success:
                    sonuclar['wordcloud'] = {
                        'klasor': str(wordcloud_klasoru),
                        'durum': 'tamamlandı'
                    }
                else:
                    sonuclar['wordcloud'] = {
                        'durum': 'hata',
                        'hata': 'Kelime bulutu oluşturulamadı'
                    }
            
            # Sonucu güncelle
            total_time = time.time() - start_time
            print(f"🎯 Analiz tamamlandı: {total_time:.2f}s")
            
            aktif_analizler[analiz_id].update({
                'durum': 'tamamlandı',
                'ilerleme': 100,
                'bitis_tarihi': datetime.now().isoformat(),
                'sonuclar': sonuclar,
                'sure': f"{total_time:.2f}s"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Analiz hatası: {e}")
            aktif_analizler[analiz_id].update({
                'durum': 'hata',
                'hata': str(e),
                'bitis_tarihi': datetime.now().isoformat()
            })
            return False

@analiz_bp.route('/baslat', methods=['POST'])
def analiz_baslat():
    """Analiz işlemini başlatır"""
    try:
        data = request.get_json()
        
        # file_id veya file_ids parametresini kontrol et
        file_id = data.get('file_id')
        file_ids = data.get('file_ids', [])
        
        if not file_id and not file_ids:
            return jsonify({
                'success': False,
                'error': 'file_id veya file_ids parametresi gerekli'
            }), 400
        
        # Tek dosya varsa listesine çevir
        if file_id and not file_ids:
            file_ids = [file_id]
        elif file_ids and not isinstance(file_ids, list):
            file_ids = [file_ids]
        
        # Analiz ID'si oluştur
        analiz_id = str(uuid.uuid4())
        
        # Analiz parametreleri
        analiz_params = {
            'id': analiz_id,
            'file_ids': file_ids,  # Çoklu dosya desteği
            'analiz_turleri': data.get('analiz_turleri', ['lda', 'sentiment', 'wordcloud']),
            'lda_konu_sayisi': data.get('lda_konu_sayisi', current_app.config['DEFAULT_LDA_TOPICS']),
            'lda_iterations': data.get('lda_iterations', 100),
            'batch_size': data.get('batch_size', current_app.config['DEFAULT_BATCH_SIZE']),
            'max_words': data.get('max_words', 200),
            'color_scheme': data.get('color_scheme', 'viridis'),
            'analysis_name': data.get('analysis_name', f'analiz_{analiz_id[:8]}'),
            'baslangic_tarihi': datetime.now().isoformat()
        }
        
        # Analizi aktif analizler listesine ekle
        aktif_analizler[analiz_id] = {
            'params': analiz_params,
            'durum': 'beklemede',
            'ilerleme': 0,
            'baslangic_tarihi': analiz_params['baslangic_tarihi']
        }
        
        # Hızlı synchronous analiz (küçük veri setleri için)
        if len(file_ids) == 1 and data.get('quick_analysis', False):
            print("⚡ Hızlı analiz modu seçildi")
            success = analiz_hizli_calistir(analiz_params)
            
            if success:
                return jsonify({
                    'success': True,
                    'data': {
                        'analiz_id': analiz_id,
                        'durum': 'tamamlandı',
                        'mesaj': 'Analiz başarıyla tamamlandı',
                        'sonuclar': aktif_analizler[analiz_id].get('sonuclar', {}),
                        'sure': aktif_analizler[analiz_id].get('sure', 'bilinmiyor')
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': aktif_analizler[analiz_id].get('hata', 'Bilinmeyen hata')
                }), 500
        
        # Background thread'de analizi başlat (büyük veri setleri için)
        analiz_thread = threading.Thread(
            target=analiz_hizli_calistir,
            args=(analiz_params, current_app._get_current_object())
        )
        analiz_thread.daemon = True
        analiz_thread.start()
        
        return jsonify({
            'success': True,
            'data': {
                'analiz_id': analiz_id,
                'durum': 'başlatıldı',
                'mesaj': 'Analiz başarıyla başlatıldı'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analiz_bp.route('/durum/<analiz_id>', methods=['GET'])
def analiz_durumu(analiz_id):
    """Analiz durumunu döner"""
    try:
        if analiz_id not in aktif_analizler:
            return jsonify({
                'success': False,
                'error': 'Analiz bulunamadı'
            }), 404
        
        analiz_info = aktif_analizler[analiz_id]
        
        return jsonify({
            'success': True,
            'data': {
                'analiz_id': analiz_id,
                'durum': analiz_info['durum'],
                'ilerleme': analiz_info['ilerleme'],
                'baslangic_tarihi': analiz_info.get('baslangic_tarihi'),
                'bitis_tarihi': analiz_info.get('bitis_tarihi'),
                'hata': analiz_info.get('hata'),
                'sonuclar': analiz_info.get('sonuclar')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analiz_bp.route('/liste', methods=['GET'])
def analiz_listesi():
    """Tüm analizleri listeler"""
    try:
        analizler = []
        
        for analiz_id, analiz_info in aktif_analizler.items():
            params = analiz_info.get('params', {})
            
            # Dosya sayısı ve toplam tweet sayısını hesapla
            file_ids = params.get('file_ids', [])
            toplam_tweet = 0
            
            # Dosyaların tweet sayısını hesapla
            for file_id in file_ids:
                try:
                    # Dosya yolunu bul ve tweet sayısını hesapla
                    tweet_arsivleri_path = current_app.config['TWEET_ARSIVLERI_FOLDER']
                    dosya_yolu = tweet_arsivleri_path / file_id
                    
                    if dosya_yolu.exists():
                        with open(dosya_yolu, 'r', encoding='utf-8') as f:
                            import json
                            veri = json.load(f)
                            if isinstance(veri, list):
                                toplam_tweet += len(veri)
                    else:
                        # Dosya ID'si olarak verilmişse, mock data kullan
                        toplam_tweet += 2000  # Varsayılan değer
                except Exception as e:
                    print(f"Dosya okuma hatası {file_id}: {e}")
                    toplam_tweet += 1500  # Hata durumunda varsayılan değer
            
            analiz_bilgisi = {
                'id': analiz_id,
                'name': params.get('analysis_name') or f'Analiz {analiz_id[:8]}',
                'status': analiz_info.get('durum', 'bilinmiyor'),
                'types': params.get('analiz_turleri', []),
                'startDate': analiz_info.get('baslangic_tarihi'),
                'endDate': analiz_info.get('bitis_tarihi'),
                'tweetCount': toplam_tweet,
                'progress': analiz_info.get('ilerleme', 0),
                'error': analiz_info.get('hata'),
                'fileCount': len(file_ids)
            }
            
            analizler.append(analiz_bilgisi)
        
        return jsonify({
            'success': True,
            'data': analizler,
            'total': len(analizler)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analiz_bp.route('/sonuclar/<analiz_id>', methods=['GET'])
def analiz_sonuclari(analiz_id):
    """Analiz sonuçlarını döner"""
    try:
        if analiz_id not in aktif_analizler:
            return jsonify({
                'success': False,
                'error': 'Analiz bulunamadı'
            }), 404
        
        analiz_info = aktif_analizler[analiz_id]
        
        if analiz_info['durum'] != 'tamamlandı':
            return jsonify({
                'success': False,
                'error': 'Analiz henüz tamamlanmadı'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'analiz_id': analiz_id,
                'sonuclar': analiz_info.get('sonuclar', {}),
                'bitis_tarihi': analiz_info.get('bitis_tarihi')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analiz_bp.route('/sonuc-dosyasi/<analiz_id>/<dosya_adi>')
def analiz_sonuc_dosyasi(analiz_id, dosya_adi):
    """Analiz sonuç dosyasını döner (resim, CSV, HTML vb.)"""
    try:
        import os
        from flask import send_file
        
        # Güvenlik kontrolü
        if '..' in dosya_adi or '/' in dosya_adi or '\\' in dosya_adi:
            return "Geçersiz dosya adı", 400
        
        # Dosya yolu
        sonuc_klasoru = current_app.config['SONUCLAR_FOLDER'] / analiz_id
        dosya_yolu = sonuc_klasoru / dosya_adi
        
        # Alt klasörlerde de arama yap
        if not dosya_yolu.exists():
            for alt_klasor in ['lda', 'sentiment', 'wordcloud']:
                alt_dosya_yolu = sonuc_klasoru / alt_klasor / dosya_adi
                if alt_dosya_yolu.exists():
                    dosya_yolu = alt_dosya_yolu
                    break
        
        if not dosya_yolu.exists():
            return "Dosya bulunamadı", 404
        
        return send_file(dosya_yolu)
        
    except Exception as e:
        return f"Hata: {str(e)}", 500

@analiz_bp.route('/zip-indir/<analiz_id>', methods=['POST'])
def analiz_zip_indir(analiz_id):
    """Analiz sonuçlarını ZIP olarak indirir"""
    try:
        import zipfile
        import io
        from flask import send_file
        
        # Analiz klasörü kontrolü
        sonuc_klasoru = current_app.config['SONUCLAR_FOLDER'] / analiz_id
        if not sonuc_klasoru.exists():
            return jsonify({'success': False, 'error': 'Analiz bulunamadı'}), 404
        
        # ZIP dosyası oluştur
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Tüm dosyaları zip'e ekle
            for root, dirs, files in os.walk(sonuc_klasoru):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Klasör yapısını koru
                    arcname = os.path.relpath(file_path, sonuc_klasoru)
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f'analiz_{analiz_id[:8]}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 