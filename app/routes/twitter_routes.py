"""
Twitter Veri Çekme Route'ları
============================

Twitter'dan veri çekme işlemlerini yöneten route'lar.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from twikit import Client
import threading
import time

twitter_bp = Blueprint('twitter', __name__)

# Global değişkenler - işlem durumunu takip etmek için
fetching_status = {
    'is_active': False,
    'progress': 0,
    'total_tweets': 0,
    'current_tweets': 0,
    'username': '',
    'message': '',
    'filename': ''
}

@twitter_bp.route('/twitter-veri-cekme')
def twitter_veri_cekme():
    """Twitter veri çekme sayfası"""
    return render_template('twitter_veri_cekme.html',
                         title='Twitter Veri Çekme',
                         page='twitter-veri-cekme')

@twitter_bp.route('/twitter-veri-cekme/basla', methods=['POST'])
def twitter_veri_cekme_basla():
    """Twitter veri çekme işlemini başlat"""
    global fetching_status
    
    if fetching_status['is_active']:
        return jsonify({
            'success': False,
            'message': 'Zaten bir veri çekme işlemi devam ediyor!'
        }), 400
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        tweet_count = int(data.get('tweet_count', 100))
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı adı boş olamaz!'
            }), 400
            
        if tweet_count <= 0 or tweet_count > 5000:
            return jsonify({
                'success': False,
                'message': 'Tweet sayısı 1-5000 arasında olmalıdır!'
            }), 400
        
        # İşlem durumunu sıfırla
        fetching_status.update({
            'is_active': True,
            'progress': 0,
            'total_tweets': tweet_count,
            'current_tweets': 0,
            'username': username,
            'message': 'Twitter\'a giriş yapılıyor...',
            'filename': ''
        })
        
        # Flask app context'ini thread'e aktar
        app = current_app._get_current_object()
        config_data = {
            'BASEDIR': current_app.config['BASEDIR'],
            'TWEET_ARSIVLERI_FOLDER': current_app.config['TWEET_ARSIVLERI_FOLDER']
        }
        
        # Asenkron işlemi ayrı thread'de başlat
        thread = threading.Thread(
            target=lambda: asyncio.run(fetch_tweets_async(username, tweet_count, app, config_data))
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Veri çekme işlemi başlatıldı!'
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Tweet sayısı geçerli bir sayı olmalıdır!'
        }), 400
    except Exception as e:
        fetching_status['is_active'] = False
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}'
        }), 500

@twitter_bp.route('/twitter-veri-cekme/durum')
def twitter_veri_cekme_durum():
    """Twitter veri çekme işleminin durumunu döndür"""
    global fetching_status
    return jsonify(fetching_status)

@twitter_bp.route('/twitter-veri-cekme/dosyalar')
def twitter_dosyalar():
    """Çekilen Twitter dosyalarını listele"""
    try:
        tweet_arsivleri_path = current_app.config['TWEET_ARSIVLERI_FOLDER']
        dosyalar = []
        
        if tweet_arsivleri_path.exists():
            for dosya in tweet_arsivleri_path.glob('*.json'):
                try:
                    dosya_boyutu = dosya.stat().st_size
                    dosya_tarihi = dosya.stat().st_mtime
                    
                    with open(dosya, 'r', encoding='utf-8') as f:
                        veri = json.load(f)
                        tweet_sayisi = len(veri) if isinstance(veri, list) else 0
                    
                    dosyalar.append({
                        'isim': dosya.name,
                        'boyut': format_file_size(dosya_boyutu),
                        'tarih': datetime.fromtimestamp(dosya_tarihi).strftime('%d.%m.%Y %H:%M'),
                        'tweet_sayisi': tweet_sayisi,
                        'username': dosya.stem.replace('_tweets', '')
                    })
                except Exception as e:
                    print(f"Dosya okuma hatası {dosya.name}: {e}")
        
        # En yeni dosyalar önce gelsin
        dosyalar.sort(key=lambda x: x['tarih'], reverse=True)
        
        return jsonify({
            'success': True,
            'dosyalar': dosyalar
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Dosyalar yüklenirken hata: {str(e)}'
        }), 500

async def fetch_tweets_async(username, tweet_count, app, config_data):
    """Asenkron Twitter veri çekme fonksiyonu"""
    global fetching_status
    
    try:
        # Twitter istemcisini oluştur
        client = Client(language='tr-TR')
        
        # Cookie dosyası yolu
        cookie_file = Path(config_data['BASEDIR']) / 'twikit_sandbox' / 'twikit_cookies.json'
        
        # Twitter giriş bilgileri - güvenlik için environment variable'lardan alınmalı
        USERNAME = "DiziSeyt"
        EMAIL = "dizifilmizle420@outlook.com"
        PASSWORD = "14987abc"
        
        logged_in_via_cookie = False
        
        # Cookie ile giriş deneme
        if cookie_file.exists():
            try:
                client.load_cookies(str(cookie_file))
                fetching_status['message'] = 'Oturum bilgileri yüklendi, test ediliyor...'
                
                # Cookie'nin çalışıp çalışmadığını test et
                try:
                    test_user = await client.get_user_by_screen_name('twitter')
                    if test_user:
                        logged_in_via_cookie = True
                        fetching_status['message'] = 'Mevcut oturum geçerli'
                    else:
                        raise Exception("Cookie test failed")
                except Exception as cookie_test_error:
                    fetching_status['message'] = 'Mevcut oturum geçersiz, yeni giriş yapılıyor...'
                    if cookie_file.exists():
                        cookie_file.unlink(missing_ok=True)
                    client = Client(language='tr-TR')
            except Exception as e:
                fetching_status['message'] = 'Cookie yüklenirken hata, yeni giriş yapılıyor...'
                if cookie_file.exists():
                    cookie_file.unlink(missing_ok=True)
                client = Client(language='tr-TR')
        
        # Gerekirse kullanıcı adı/şifre ile giriş
        if not logged_in_via_cookie:
            fetching_status['message'] = 'Twitter\'a yeni giriş yapılıyor...'
            try:
                await client.login(
                    auth_info_1=USERNAME,
                    auth_info_2=EMAIL,
                    password=PASSWORD
                )
                client.save_cookies(str(cookie_file))
                fetching_status['message'] = 'Giriş başarılı, oturum kaydedildi'
            except Exception as login_error:
                fetching_status.update({
                    'is_active': False,
                    'message': f'Twitter giriş hatası: {str(login_error)}'
                })
                return
        
        # Kullanıcıyı bul
        fetching_status['message'] = f'@{username} kullanıcısı aranıyor...'
        target_user = await client.get_user_by_screen_name(username)
        
        if not target_user:
            fetching_status.update({
                'is_active': False,
                'message': f'@{username} kullanıcısı bulunamadı!'
            })
            return
        
        # Tweet çekme işlemi
        fetching_status['message'] = f'@{username} kullanıcısının tweetleri çekiliyor...'
        all_tweet_texts = []
        
        try:
            current_page = await target_user.get_tweets('Tweets', count=min(tweet_count, 20))
            page_count = 0
            
            while current_page and len(all_tweet_texts) < tweet_count:
                page_count += 1
                fetching_status['message'] = f'{page_count}. sayfa işleniyor...'
                
                tweets_in_this_page = 0
                for tweet in current_page:
                    if len(all_tweet_texts) < tweet_count:
                        all_tweet_texts.append(tweet.text)
                        tweets_in_this_page += 1
                        
                        # Progress güncelle
                        fetching_status['current_tweets'] = len(all_tweet_texts)
                        fetching_status['progress'] = int((len(all_tweet_texts) / tweet_count) * 100)
                    else:
                        break
                
                # Rate limiting için kısa bekleme
                if len(all_tweet_texts) < tweet_count and tweets_in_this_page > 0:
                    fetching_status['message'] = f'Sonraki sayfa için bekleniyor... ({len(all_tweet_texts)}/{tweet_count})'
                    await asyncio.sleep(2)  # 2 saniye bekle
                    
                    try:
                        next_page_data = await current_page.next()
                        if next_page_data and len(next_page_data) > 0:
                            current_page = next_page_data
                        else:
                            break
                    except Exception as page_error:
                        fetching_status['message'] = f'Sayfa yükleme hatası: {str(page_error)}'
                        break
                else:
                    break
                    
        except Exception as tweets_error:
            if "rate limit" in str(tweets_error).lower():
                fetching_status.update({
                    'is_active': False,
                    'message': f'Twitter rate limit aşıldı. Lütfen 15 dakika sonra tekrar deneyin.'
                })
                return
            else:
                fetching_status.update({
                    'is_active': False,
                    'message': f'Tweet çekme hatası: {str(tweets_error)}'
                })
                return
        
        # Dosyayı kaydet
        if all_tweet_texts:
            output_filename = f"{username}_tweets.json"
            output_path = config_data['TWEET_ARSIVLERI_FOLDER'] / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_tweet_texts[:tweet_count], f, ensure_ascii=False, indent=2)
            
            fetching_status.update({
                'is_active': False,
                'progress': 100,
                'message': f'Başarıyla tamamlandı! {len(all_tweet_texts)} tweet kaydedildi.',
                'filename': output_filename
            })
        else:
            fetching_status.update({
                'is_active': False,
                'message': f'@{username} kullanıcısının tweeti bulunamadı!'
            })
        
        # Oturumu kapat
        try:
            await client.logout()
        except:
            pass
            
    except Exception as e:
        error_message = str(e)
        
        # Spesifik hata türlerine göre mesaj oluştur
        if "401" in error_message or "authenticate" in error_message.lower():
            final_message = "Twitter kimlik doğrulama hatası. Hesap bilgileri kontrol edilmelidir."
        elif "rate limit" in error_message.lower() or "429" in error_message:
            final_message = "Twitter rate limit aşıldı. 15 dakika sonra tekrar deneyin."
        elif "403" in error_message or "forbidden" in error_message.lower():
            final_message = "Bu işlem için izin yok. Hesap kısıtlanmış olabilir."
        elif "404" in error_message or "not found" in error_message.lower():
            final_message = f"@{username} kullanıcısı bulunamadı veya erişilemiyor."
        elif "timeout" in error_message.lower():
            final_message = "Bağlantı zaman aşımı. İnternet bağlantınızı kontrol edin."
        elif "connection" in error_message.lower():
            final_message = "Bağlantı hatası. İnternet bağlantınızı kontrol edin."
        else:
            final_message = f"Beklenmeyen hata: {error_message[:100]}..."
        
        fetching_status.update({
            'is_active': False,
            'message': final_message
        })

def format_file_size(bytes_size):
    """Dosya boyutunu insan okunabilir formata çevirir"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB" 