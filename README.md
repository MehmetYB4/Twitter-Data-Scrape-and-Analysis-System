# 🐦 Twitter Analiz Platformu

Modern ve kapsamlı bir Twitter veri analizi ve doğal dil işleme platformu. Bu proje, Twitter verilerinizi derinlemesine analiz etmenizi sağlayan kullanıcı dostu bir web uygulamasıdır.

## 🌟 Özellikler

### 📊 Analiz Türleri
- **LDA Konu Modelleme**: Tweet'lerdeki gizli konuları keşfetme
- **Duygu Analizi**: Turkish BERT ile pozitif/negatif/nötr duygu sınıflandırması  
- **Kelime Bulutu**: En sık kullanılan kelimelerin görsel analizi

### 🚀 Platform Özellikleri
- **Modern Web Arayüzü**: Bootstrap 5 ile responsive tasarım
- **Real-time Progress Tracking**: Canlı analiz ilerleme takibi
- **Çoklu Dosya Desteği**: Birden fazla Twitter arşivini aynı anda analiz
- **Gelişmiş Ön İşleme**: 200+ Türkçe stopword ile optimize edilmiş metin işleme
- **Etkileşimli Sonuçlar**: HTML ve PNG formatında çıktılar
- **AI Yorumlu Raporlar**: Otomatik PDF rapor oluşturma
- **Analiz Geçmişi**: Tüm analizlerinizi kaydetme ve yönetme

### 🔧 Teknik Özellikler
- **Modüler Mimari**: Bağımsız analiz modülleri
- **Asenkron İşleme**: Background thread'ler ile performanslı analiz
- **Hata Yönetimi**: Kapsamlı hata yakalama ve fallback mekanizmaları
- **Güvenlik**: Dosya validasyonu ve güvenli yükleme
- **API Desteği**: RESTful API endpoints

## 🛠️ Kurulum

### Sistem Gereksinimleri
- Python 3.8+
- 4GB+ RAM (duygu analizi için)
- 2GB+ disk alanı

### Hızlı Kurulum

```bash
# Repository'yi klonlayın
git clone <repository-url>
cd VeriCekmeDahilEtme

# Gerekli paketleri kurun
pip install -r requirements.txt

# Uygulamayı başlatın
python run.py
```

### Detaylı Kurulum

1. **Python Bağımlılıkları**
```bash
pip install flask pandas scikit-learn transformers torch
pip install wordcloud matplotlib seaborn gensim
pip install reportlab beautifulsoup4 requests
```

2. **Klasör Yapısını Oluşturun**
```bash
mkdir tweet_arsivleri
mkdir sonuclar
mkdir static/uploads
```

3. **Konfigürasyon**
`config.py` dosyasında gerekli ayarları yapın.

## 📂 Proje Yapısı

```
VeriCekmeDahilEtme/
├── analiz/                 # Analiz modülleri
│   ├── lda/               # LDA konu modelleme
│   ├── sentiment/         # Duygu analizi
│   ├── wordcloud/         # Kelime bulutu
│   └── preprocessing.py   # Gelişmiş ön işleme
├── app/                   # Flask web uygulaması
│   ├── routes/           # Route tanımları
│   ├── templates/        # HTML şablonları
│   └── static/           # CSS, JS, resimler
├── tweet_arsivleri/      # Twitter veri dosyaları
├── sonuclar/             # Analiz sonuçları
├── run.py               # Ana uygulama dosyası
└── requirements.txt     # Python bağımlılıkları
```

## 🎯 Kullanım

### 1. Veri Hazırlama
- Twitter arşiv dosyalarınızı `tweet_arsivleri/` klasörüne koyun
- Desteklenen format: JSON (Twitter API formatı)

### 2. Analiz Süreci
1. **Veri Seçimi**: Analiz edilecek dosyaları seçin
2. **Konfigürasyon**: Analiz türlerini ve parametreleri ayarlayın
3. **Analiz Başlatma**: "Analizi Başlat" butonuna tıklayın
4. **Progress Tracking**: Real-time ilerleme takibi
5. **Sonuç İnceleme**: Detaylı analiz sonuçlarını görüntüleyin

### 3. Sonuç Formatları
- **LDA**: Etkileşimli HTML görselleştirme
- **Duygu Analizi**: PNG grafikleri + CSV verileri
- **Kelime Bulutu**: PNG görsel + CSV kelime listeleri
- **Tam Rapor**: AI yorumlu PDF rapor

## 🔬 Analiz Detayları

### LDA Konu Modelleme
- Gensim LDA implementasyonu
- 2-8 arası konu sayısı desteği
- pyLDAvis ile etkileşimli görselleştirme
- Konu-belge dağılım matrisleri

### Duygu Analizi
- Turkish BERT pre-trained model
- 3 sınıf: Pozitif, Negatif, Nötr
- Batch processing ile hızlı analiz
- Güven skorları ile detaylı sonuçlar

### Kelime Bulutu
- Gelişmiş Türkçe metin ön işleme
- 200+ stopword filtreleme
- Farklı renk şemaları
- Frekans bazlı boyutlandırma

## 📈 Performans

### Analiz Süreleri (tahmini)
- **100 tweet**: ~30 saniye
- **1000 tweet**: ~2 dakika
- **5000 tweet**: ~8 dakika
- **10000+ tweet**: ~15+ dakika

### Optimizasyon İpuçları
- LDA konu sayısını düşük tutun (2-5)
- Duygu analizi için batch size'ı artırın
- Küçük dosyalar için "Hızlı Analiz" modunu kullanın

## 🔧 Konfigürasyon

### Analiz Parametreleri
```python
# LDA Ayarları
LDA_TOPICS = 5          # Konu sayısı
LDA_ITERATIONS = 20     # Iterasyon sayısı

# Duygu Analizi
BATCH_SIZE = 16         # Batch büyüklüğü
SENTIMENT_MODEL = "turkish-bert"

# Kelime Bulutu
MAX_WORDS = 100         # Maksimum kelime
COLOR_SCHEME = "viridis"
```

### Sunucu Ayarları
```python
# Flask Konfigürasyonu
DEBUG = True
PORT = 5000
HOST = "localhost"

# Dosya Yolları
TWEET_ARSIVLERI_FOLDER = "tweet_arsivleri"
SONUCLAR_FOLDER = "sonuclar"
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**1. Analiz başlamıyor**
- Console'da hata mesajlarını kontrol edin
- Dosya seçimini doğrulayın
- Internet bağlantınızı kontrol edin

**2. Duygu analizi yavaş**
- Batch size'ı düşürün (8-16)
- RAM kullanımını kontrol edin
- GPU kullanımını aktifleştirin (opsiyonel)

**3. Kelime bulutu boş**
- Stopword listesini kontrol edin
- Minimum kelime uzunluğunu düşürün
- Veri kalitesini kontrol edin

### Debug Modu
```bash
# Debug modunda çalıştırma
export FLASK_ENV=development
python run.py
```

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

### Kullanılan Kütüphaneler
- **Flask**: Web framework
- **Transformers**: Turkish BERT modeli
- **Gensim**: LDA konu modelleme
- **Scikit-learn**: Makine öğrenmesi
- **WordCloud**: Kelime bulutu oluşturma
- **Bootstrap**: Modern UI framework

### Veri Kaynakları
- Turkish BERT modeli: `dbmdz/bert-base-turkish-cased`
- Türkçe stopword listeleri
- Twitter API format desteği

## 📞 İletişim

Sorularınız için:
- Issue açın: GitHub Issues
- Dokumentasyon: Bu README dosyası
- Wiki: Proje wiki sayfaları

---

**🚀 Twitter verilerinizi analiz etmeye başlayın!**

*Bu platform, doğal dil işleme ve makine öğrenmesi teknikleriyle Twitter verilerinizden değerli içgörüler elde etmenizi sağlar.* 