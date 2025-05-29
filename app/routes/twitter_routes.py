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

@twitter_bp.route('/twitter-veri-cekme/reset-cookies', methods=['POST'])
def twitter_reset_cookies():
    """Twitter cookies'leri temizle ve güvenlik sıfırlaması yap"""
    try:
        cookie_file = current_app.config['BASEDIR'] / 'twikit_sandbox' / 'twikit_cookies.json'
        
        # Cookie dosyasını sil
        if cookie_file.exists():
            cookie_file.unlink()
            return jsonify({
                'success': True,
                'message': 'Oturum bilgileri temizlendi. Yeni giriş yapılacak.'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Zaten temiz oturum.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Oturum temizlenirken hata: {str(e)}'
        }), 500

@twitter_bp.route('/twitter-veri-cekme/iptal', methods=['POST'])
def twitter_veri_cekme_iptal():
    """Devam eden Twitter veri çekme işlemini iptal et"""
    global fetching_status
    
    try:
        if fetching_status['is_active']:
            fetching_status.update({
                'is_active': False,
                'message': 'İşlem kullanıcı tarafından iptal edildi.'
            })
            return jsonify({
                'success': True,
                'message': 'Veri çekme işlemi iptal edildi.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Şu anda aktif bir işlem yok.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'İptal işleminde hata: {str(e)}'
        }), 500

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
    """Asenkron Twitter veri çekme fonksiyonu - Güvenlik iyileştirmeli"""
    global fetching_status
    
    try:
        # Twitter istemcisini oluştur - User-Agent ve diğer güvenlik ayarları
        client = Client(language='tr-TR')
        
        # Cookie dosyası yolu
        cookie_file = Path(config_data['BASEDIR']) / 'twikit_sandbox' / 'twikit_cookies.json'
        
        # Twitter giriş bilgileri - güvenlik için environment variable'lardan alınmalı
        USERNAME = "DTest2025"
        EMAIL = "twitterdeneme2025@outlook.com"
        PASSWORD = "14987abc"
        
        logged_in_via_cookie = False
        
        # Önce uzun bir bekleme süresi ekle (güvenlik için)
        fetching_status['message'] = 'Güvenlik kontrolü, beklenilen süre: 10 saniye...'
        await asyncio.sleep(10)  # 10 saniye güvenlik beklemesi
        
        # Cookie ile giriş deneme - Daha dikkatli yaklaşım
        if cookie_file.exists():
            try:
                client.load_cookies(str(cookie_file))
                fetching_status['message'] = 'Kayıtlı oturum bilgileri test ediliyor...'
                
                # Cookie geçerliliğini test et - Rate limit'e dikkat et
                await asyncio.sleep(3)  # Test öncesi bekleme
                try:
                    test_user = await client.get_user_by_screen_name('twitter')
                    if test_user:
                        logged_in_via_cookie = True
                        fetching_status['message'] = 'Kayıtlı oturum geçerli - devam ediliyor'
                        await asyncio.sleep(2)  # Başarı sonrası güvenlik beklemesi
                    else:
                        raise Exception("Cookie geçerliliği doğrulanamadı")
                except Exception as cookie_test_error:
                    fetching_status['message'] = 'Kayıtlı oturum geçersiz, yenileniyor...'
                    if cookie_file.exists():
                        cookie_file.unlink(missing_ok=True)
                    client = Client(language='tr-TR')
                    await asyncio.sleep(5)  # Yenileme sonrası bekleme
            except Exception as e:
                fetching_status['message'] = 'Oturum yüklenirken sorun, yeni giriş yapılacak...'
                if cookie_file.exists():
                    cookie_file.unlink(missing_ok=True)
                client = Client(language='tr-TR')
                await asyncio.sleep(5)
        
        # Gerekirse kullanıcı adı/şifre ile giriş - Çok dikkatli
        if not logged_in_via_cookie:
            fetching_status['message'] = 'Yeni oturum açılıyor... Bu 30-60 saniye sürebilir.'
            
            # Çok yavaş giriş - Twitter'ın güvenlik algılamasını önlemek için
            await asyncio.sleep(15)  # Giriş öncesi uzun bekleme
            
            try:
                await client.login(
                    auth_info_1=USERNAME,
                    auth_info_2=EMAIL,
                    password=PASSWORD
                )
                
                # Giriş sonrası güvenlik beklemesi
                await asyncio.sleep(20)  # 20 saniye giriş sonrası bekleme
                
                client.save_cookies(str(cookie_file))
                fetching_status['message'] = 'Giriş başarılı, oturum güvenli şekilde kaydedildi'
                
                # Ek güvenlik beklemesi
                await asyncio.sleep(10)
                
            except Exception as login_error:
                error_msg = str(login_error)
                
                # Güvenlik bloğu kontrolü
                if any(keyword in error_msg.lower() for keyword in ['blok', 'block', 'suspend', 'restrict', 'geblokkeerd']):
                    fetching_status.update({
                        'is_active': False,
                        'message': 'Twitter hesabı güvenlik nedeniyle bloklanmış. Lütfen web tarayıcısından Twitter\'a giriş yapıp hesap doğrulamayı tamamlayın, sonra 24 saat bekleyip tekrar deneyin.'
                    })
                elif 'rate limit' in error_msg.lower() or '429' in error_msg:
                    fetching_status.update({
                        'is_active': False,
                        'message': 'Twitter rate limit aşıldı. 1 saat bekleyip tekrar deneyin.'
                    })
                elif 'captcha' in error_msg.lower():
                    fetching_status.update({
                        'is_active': False,
                        'message': 'CAPTCHA doğrulaması gerekli. Web tarayıcısından Twitter\'a giriş yapın.'
                    })
                else:
                    fetching_status.update({
                        'is_active': False,
                        'message': f'Giriş hatası: {error_msg[:200]}... Hesap bilgilerini kontrol edin.'
                    })
                return
        
        # Kullanıcı arama - Çok dikkatli
        fetching_status['message'] = f'@{username} kullanıcısı aranıyor... Güvenlik beklemesi yapılıyor.'
        await asyncio.sleep(8)  # Kullanıcı arama öncesi bekleme
        
        try:
            target_user = await client.get_user_by_screen_name(username)
        except Exception as user_error:
            fetching_status.update({
                'is_active': False,
                'message': f'@{username} kullanıcısı bulunamadı veya erişilemiyor: {str(user_error)[:100]}'
            })
            return
        
        if not target_user:
            fetching_status.update({
                'is_active': False,
                'message': f'@{username} kullanıcısı bulunamadı!'
            })
            return
        
        # Tweet çekme işlemi - ÇOK dikkatli ve yavaş
        fetching_status['message'] = f'@{username} kullanıcısının tweetleri çekiliyor... Güvenlik protokolü aktif.'
        all_tweet_texts = []
        
        try:
            # İlk sayfa - küçük batch size
            initial_count = min(tweet_count, 10)  # İlk seferde sadece 10 tweet
            current_page = await target_user.get_tweets('Tweets', count=initial_count)
            
            await asyncio.sleep(10)  # İlk sayfa sonrası uzun bekleme
            
            page_count = 0
            consecutive_failures = 0
            
            while current_page and len(all_tweet_texts) < tweet_count and consecutive_failures < 3:
                page_count += 1
                fetching_status['message'] = f'Sayfa {page_count} işleniyor... Güvenlik beklemesi yapılıyor.'
                
                tweets_in_this_page = 0
                try:
                    for tweet in current_page:
                        if len(all_tweet_texts) < tweet_count:
                            all_tweet_texts.append(tweet.text)
                            tweets_in_this_page += 1
                            
                            # Progress güncelle
                            fetching_status['current_tweets'] = len(all_tweet_texts)
                            fetching_status['progress'] = int((len(all_tweet_texts) / tweet_count) * 100)
                        else:
                            break
                    
                    consecutive_failures = 0  # Başarılı sayfa, reset et
                    
                except Exception as page_process_error:
                    consecutive_failures += 1
                    fetching_status['message'] = f'Sayfa işleme hatası (Deneme {consecutive_failures}/3): {str(page_process_error)[:50]}'
                    await asyncio.sleep(15)  # Hata sonrası uzun bekleme
                    continue
                
                # Sonraki sayfa için çok uzun bekleme
                if len(all_tweet_texts) < tweet_count and tweets_in_this_page > 0:
                    wait_time = 15 + (page_count * 5)  # Her sayfa için artan bekleme süresi
                    fetching_status['message'] = f'Güvenlik protokolü: {wait_time} saniye bekleniyor... ({len(all_tweet_texts)}/{tweet_count})'
                    await asyncio.sleep(wait_time)
                    
                    try:
                        next_page_data = await current_page.next()
                        if next_page_data and len(next_page_data) > 0:
                            current_page = next_page_data
                        else:
                            fetching_status['message'] = 'Tüm sayfalar tamamlandı.'
                            break
                    except Exception as page_error:
                        consecutive_failures += 1
                        error_msg = str(page_error)
                        
                        if 'rate limit' in error_msg.lower():
                            fetching_status['message'] = f'Rate limit - 5 dakika bekleniyor...'
                            await asyncio.sleep(300)  # 5 dakika bekle
                        else:
                            fetching_status['message'] = f'Sayfa yükleme hatası: {error_msg[:50]}'
                            await asyncio.sleep(30)  # Hata sonrası 30 saniye bekle
                else:
                    break
                    
        except Exception as tweets_error:
            error_msg = str(tweets_error)
            if "rate limit" in error_msg.lower():
                fetching_status.update({
                    'is_active': False,
                    'message': f'Twitter rate limit aşıldı. En az 1 saat sonra tekrar deneyin. Toplanan tweet: {len(all_tweet_texts)}'
                })
            elif any(keyword in error_msg.lower() for keyword in ['block', 'suspend', 'restrict']):
                fetching_status.update({
                    'is_active': False,
                    'message': f'Hesap kısıtlandı. Web tarayıcısından Twitter\'a giriş yapıp doğrulamayı tamamlayın.'
                })
            else:
                fetching_status.update({
                    'is_active': False,
                    'message': f'Tweet çekme hatası: {error_msg[:100]}... Toplanan tweet: {len(all_tweet_texts)}'
                })
            
            # Hata durumunda bile topladığımız tweetleri kaydet
            if all_tweet_texts:
                output_filename = f"{username}_tweetler_kismi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_path = config_data['TWEET_ARSIVLERI_FOLDER'] / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(all_tweet_texts, f, ensure_ascii=False, indent=2)
                
                fetching_status['filename'] = output_filename
                fetching_status['message'] += f" Kısmi veri kaydedildi: {output_filename}"
            
            return
        
        # Dosyayı kaydet
        if all_tweet_texts:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{username}_tweetleri_{timestamp}.json"
            output_path = config_data['TWEET_ARSIVLERI_FOLDER'] / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_tweet_texts[:tweet_count], f, ensure_ascii=False, indent=2)
            
            fetching_status.update({
                'is_active': False,
                'progress': 100,
                'message': f'✅ Başarıyla tamamlandı! {len(all_tweet_texts)} tweet güvenli şekilde kaydedildi.',
                'filename': output_filename
            })
        else:
            fetching_status.update({
                'is_active': False,
                'message': f'@{username} kullanıcısının tweeti bulunamadı veya erişilemiyor!'
            })
        
        # Güvenli çıkış
        try:
            await asyncio.sleep(5)  # Çıkış öncesi bekleme
            await client.logout()
        except:
            pass
            
    except Exception as e:
        error_message = str(e)
        
        # Spesifik hata türlerine göre mesaj oluştur
        if any(keyword in error_message.lower() for keyword in ['blok', 'block', 'suspend', 'geblokkeerd', 'inlogpoging']):
            final_message = "🔒 Twitter hesabı güvenlik nedeniyle geçici olarak kısıtlandı. Çözüm: 1) Web tarayıcısından Twitter.com'a giriş yapın 2) Güvenlik doğrulamasını tamamlayın 3) 24 saat bekleyin 4) Tekrar deneyin."
        elif "401" in error_message or "authenticate" in error_message.lower():
            final_message = "🔑 Kimlik doğrulama hatası. Hesap bilgileri kontrol edilmelidir."
        elif "rate limit" in error_message.lower() or "429" in error_message:
            final_message = "⏱️ Twitter rate limit aşıldı. En az 1 saat sonra tekrar deneyin."
        elif "403" in error_message or "forbidden" in error_message.lower():
            final_message = "🚫 Bu işlem için izin yok. Hesap geçici olarak kısıtlanmış olabilir."
        elif "404" in error_message or "not found" in error_message.lower():
            final_message = f"👤 @{username} kullanıcısı bulunamadı veya hesap gizli."
        elif "timeout" in error_message.lower():
            final_message = "⏰ Bağlantı zaman aşımı. İnternet bağlantınızı kontrol edin ve tekrar deneyin."
        elif "connection" in error_message.lower():
            final_message = "🌐 Bağlantı hatası. İnternet bağlantınızı kontrol edin."
        elif "captcha" in error_message.lower():
            final_message = "🤖 CAPTCHA doğrulaması gerekli. Web tarayıcısından Twitter'a giriş yapın."
        else:
            final_message = f"❌ Beklenmeyen hata: {error_message[:100]}..."
        
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