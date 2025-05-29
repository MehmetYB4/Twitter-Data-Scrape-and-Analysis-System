# 🐦 Twitter Veri Çekimi ve Analiz Sistemi

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/kullanici-adi/proje-adi.svg)](https://github.com/kullanici-adi/proje-adi/issues) <!-- TODO: Kullanıcı adı ve proje adını güncelleyin -->

Bu proje, Twitter platformundan belirli kullanıcıların tweet'lerini çekmek, bu verileri temizlemek ve çeşitli doğal dil işleme (NLP) teknikleriyle analiz etmek amacıyla geliştirilmiş bir Python uygulamasıdır.

<!-- Opsiyonel: Projenizin kısa bir GIF veya ekran görüntüsünü buraya ekleyebilirsiniz -->
<!-- ![Proje Arayüzü](path/to/your/screenshot.png) -->

## 🚀 Temel Özellikler

- **Veri Çekme**: Belirli bir Twitter kullanıcısının tweetlerini `twikit` kütüphanesi aracılığıyla çeker.
- **Oturum Yönetimi**: Cookie tabanlı oturum yönetimi ile tekrar tekrar giriş yapma ihtiyacını azaltır.
- **Veri Ön İşleme**: Çekilen tweet metinlerini analiz için hazırlar (URL, mention, hashtag temizliği, normalizasyon vb.).
- **Duygu Analizi**: Tweetlerin duygu yoğunluğunu (pozitif, negatif, nötr) belirler.
- **Kelime Bulutu**: En sık geçen kelimeleri görselleştirir.
- **Konu Modelleme (LDA)**: Tweetlerdeki gizli konuları ortaya çıkarır.
- **Sonuç Kaydetme**: Analiz sonuçlarını ve çekilen tweetleri JSON formatında kaydeder.
- **Web Arayüzü (Flask)**: Temel analiz işlemlerini yapmak ve sonuçları görüntülemek için basit bir web arayüzü sunar.

## 🛠️ Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yükleyicisi)

### Adımlar

1.  **Projeyi Klonlayın:**
    ```bash
    git clone https://github.com/kullanici-adi/proje-adi.git # TODO: Kendi GitHub linkinizle değiştirin
    cd proje-adi
    ```

2.  **Sanal Ortam Oluşturun (Önerilir):
    ```bash
    python -m venv .venv
    ```
    Sanal ortamı aktive edin:
    -   Windows:
        ```bash
        .venv\Scripts\activate
        ```
    -   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Gerekli Paketleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Yapılandırma (Opsiyonel):**
    - `twikit_sandbox/tweet_fetcher.py` içerisinde Twitter API erişimi için kendi kullanıcı adı, email ve şifrenizi girmeniz gerekebilir (güvenlik nedeniyle bu bilgilerin doğrudan koda yazılması önerilmez, environment variable gibi yöntemler tercih edilmelidir).
    - `config.py` dosyası varsa, web uygulaması ayarlarını oradan düzenleyebilirsiniz.

## 🎯 Kullanım

### 1. Tweet Çekme (Komut Satırı)

`tweet_fetcher.py` script'ini çalıştırarak belirli bir kullanıcının tweetlerini çekebilirsiniz:

```bash
python twikit_sandbox/tweet_fetcher.py
```
Script sizden hedef kullanıcı adını ve çekmek istediğiniz tweet sayısını isteyecektir. Sonuçlar, ana dizinde `{kullanici_adi}_tweets.json` olarak kaydedilecektir.

### 2. Web Arayüzü (Flask Uygulaması)

Web arayüzünü başlatmak için:

```bash
python run.py
```
Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır. Tarayıcınızdan bu adrese giderek:
- Tweet dosyalarını yükleyebilir,
- Çeşitli analizleri (duygu, kelime bulutu, LDA) çalıştırabilir,
- Sonuçları görüntüleyebilirsiniz.

## 📂 Proje Yapısı

```
. 
├── analiz/                 # Analiz modülleri (preprocessing, sentiment, wordcloud, lda)
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── sentiment/
│   ├── wordcloud/
│   └── lda/
├── app/                    # Flask web uygulaması
│   ├── __init__.py
│   ├── routes/             # Web route tanımları
│   ├── templates/          # HTML şablonları
│   └── utils/              # Yardımcı fonksiyonlar
├── static/                 # Web arayüzü için statik dosyalar (CSS, JS, resimler)
├── twikit_sandbox/         # Twitter veri çekme scriptleri
│   └── tweet_fetcher.py
├── tweet_arsivleri/        # Yüklenen veya çekilen tweet dosyaları (web arayüzü için)
├── sonuclar/               # Web arayüzünden yapılan analiz sonuçları
├── LICENSE                 # Proje lisansı (MIT)
├── README.md               # Bu dosya
├── requirements.txt        # Gerekli Python kütüphaneleri
├── run.py                  # Flask uygulamasını başlatan ana script
├── config.py               # (Varsa) Uygulama yapılandırma ayarları
└── .gitignore              # Git tarafından takip edilmeyecek dosyalar/klasörler
```

## 🔬 Teknik Detaylar

- **Veri Çekme**: `twikit` kütüphanesi kullanılarak asenkron olarak Twitter verileri çekilir. Cookie tabanlı oturum yönetimi ile API kullanımı optimize edilir.
- **Ön İşleme**: `analiz/preprocessing.py` içerisinde bulunan fonksiyonlar ile metinler temizlenir (URL, mention, hashtag kaldırma, küçük harfe çevirme, noktalama işaretleri ve emojilerin temizlenmesi, stop-word filtreleme).
- **Duygu Analizi**: Genellikle `TextBlob` gibi kütüphanelerle veya daha gelişmiş modellerle (örneğin, `transformers` kütüphanesinden BERT tabanlı modeller) yapılır.
- **Kelime Bulutu**: `wordcloud` kütüphanesi ile en sık geçen kelimeler görselleştirilir.
- **LDA Konu Modelleme**: `gensim` veya `scikit-learn` kütüphaneleri ile metinlerdeki gizli konular bulunur.
- **Web Framework**: `Flask` kullanılarak basit ve modüler bir web arayüzü oluşturulmuştur.

## 🤝 Katkıda Bulunma

Katkılarınız projeyi daha da geliştirmemize yardımcı olacaktır! Lütfen aşağıdaki adımları izleyin:

1.  Projeyi Fork Edin.
2.  Yeni bir Feature Branch oluşturun (`git checkout -b feature/YeniOzellik`).
3.  Değişikliklerinizi Commit edin (`git commit -m 'Yeni bir özellik eklendi'`).
4.  Branch'inizi Push edin (`git push origin feature/YeniOzellik`).
5.  Bir Pull Request açın.

Lütfen Pull Request açmadan önce kodunuzun PEP 8 standartlarına uygun olduğundan ve test edildiğinden emin olun.

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 🙏 Teşekkürler

- `twikit` kütüphanesinin geliştiricilerine.
- Projede kullanılan açık kaynak kütüphanelerin (Flask, NLTK, TextBlob, WordCloud vb.) geliştiricilerine.

---

Sorularınız veya önerileriniz için lütfen bir [Issue](https://github.com/kullanici-adi/proje-adi/issues) açmaktan çekinmeyin! <!-- TODO: Kullanıcı adı ve proje adını güncelleyin --> 