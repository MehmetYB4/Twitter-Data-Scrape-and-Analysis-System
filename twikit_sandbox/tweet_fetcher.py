import asyncio
from twikit import Client
import json
import os

async def main():
    USERNAME = "DTest2025"
    EMAIL = "twitterdeneme2025@outlook.com"
    PASSWORD = "14987abc"
    
    COOKIE_FILE = "twikit_cookies.json"

    target_username_input = input("Tweetlerini çekmek istediğiniz Twitter kullanıcı adını girin (örneğin, varank): @")
    TARGET_USERNAME = target_username_input.strip()
    if not TARGET_USERNAME:
        print("Kullanıcı adı girmediniz. Çıkılıyor.")
        return

    while True:
        try:
            tweet_count_input = input(f"@{TARGET_USERNAME} için kaç tweet çekmek istersiniz? (Örn: 100, maks ~5000 hedeflenebilir ama sınırlamalara tabidir): ")
            TWEET_COUNT = int(tweet_count_input)
            if TWEET_COUNT <= 0:
                print("Lütfen pozitif bir sayı girin.")
            else:
                break
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")

    client = Client(language='tr-TR')
    all_tweet_texts = []
    output_filename = f"{TARGET_USERNAME}_tweets.json"

    try:
        logged_in_via_cookie = False
        if os.path.exists(COOKIE_FILE):
            try:
                client.load_cookies(COOKIE_FILE)
                print(f"'{COOKIE_FILE}' dosyasından oturum bilgileri yüklendi.")
                logged_in_via_cookie = True
            except Exception as e_cookie_load: 
                print(f"'{COOKIE_FILE}' yüklenirken bir hata oluştu ({e_cookie_load}). Yeni giriş yapılacak.")
                if os.path.exists(COOKIE_FILE):
                    try:
                        os.remove(COOKIE_FILE)
                        print(f"Sorunlu cookie dosyası ('{COOKIE_FILE}') silindi.")
                    except OSError as e_remove:
                        print(f"Sorunlu cookie dosyası ('{COOKIE_FILE}') silinirken hata: {e_remove}")
                client = Client(language='tr-TR') # Reinitialize client

        if not logged_in_via_cookie:
            print("Twitter'a kullanıcı adı ve şifre ile giriş yapılıyor...")
            await client.login(
                auth_info_1=USERNAME,
                auth_info_2=EMAIL,
                password=PASSWORD
            )
            print("Giriş başarılı.")
            client.save_cookies(COOKIE_FILE)
            print(f"Oturum bilgileri '{COOKIE_FILE}' dosyasına kaydedildi.")

        print(f"@{TARGET_USERNAME} kullanıcısı aranıyor...")
        target_user = await client.get_user_by_screen_name(TARGET_USERNAME)
        if not target_user:
            print(f"@{TARGET_USERNAME} kullanıcısı bulunamadı.")
            if logged_in_via_cookie and os.path.exists(COOKIE_FILE):
                 os.remove(COOKIE_FILE)
                 print(f"@{TARGET_USERNAME} bulunamadı ve cookie ile giriş yapılmıştı. '{COOKIE_FILE}' silindi.")
            return

        print(f"@{TARGET_USERNAME} kullanıcısının yaklaşık {TWEET_COUNT} tweeti çekiliyor...")
        
        current_page = await target_user.get_tweets('Tweets', count=TWEET_COUNT)
        page_count = 0

        while current_page and len(all_tweet_texts) < TWEET_COUNT:
            page_count += 1
            print(f"{page_count}. sayfa işleniyor... (Toplam {len(all_tweet_texts)}/{TWEET_COUNT} tweet)")
            tweets_in_this_page = 0
            for tweet in current_page:
                if len(all_tweet_texts) < TWEET_COUNT:
                    all_tweet_texts.append(tweet.text)
                    tweets_in_this_page += 1
                else:
                    break
            print(f"Bu sayfadan {tweets_in_this_page} tweet eklendi.")

            if len(all_tweet_texts) < TWEET_COUNT and tweets_in_this_page > 0:
                next_page_data = await current_page.next()
                if next_page_data and len(next_page_data) > 0:
                    current_page = next_page_data
                else:
                    print("Çekilecek başka tweet kalmadı.")
                    break
            else:
                break
        
        if not all_tweet_texts:
            print(f"@{TARGET_USERNAME} kullanıcısının tweeti bulunamadı.")
        else:
            print(f"Toplam {len(all_tweet_texts)} tweet çekildi.")
            final_tweets_to_output = all_tweet_texts[:TWEET_COUNT]
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(final_tweets_to_output, f, ensure_ascii=False, indent=2)
            print(f"Tweetler '{os.path.abspath(output_filename)}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        if "authenticate" in str(e).lower() or "login" in str(e).lower() or "401" in str(e) or "403" in str(e):
            if os.path.exists(COOKIE_FILE):
                try:
                    os.remove(COOKIE_FILE)
                    print(f"Kimlik doğrulama hatası nedeniyle '{COOKIE_FILE}' dosyası silindi.")
                except OSError as e_remove:
                    print(f"'{COOKIE_FILE}' silinirken hata: {e_remove}")
    finally:
        try:
            await client.logout()
            print("Oturum kapatıldı.")
        except Exception as e_logout:
            # Potansiyel olarak client zaten kapalı veya hata oluştu, bu normal olabilir.
            pass

if __name__ == "__main__":
    asyncio.run(main()) 