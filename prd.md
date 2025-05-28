# Twitter Analiz Projesi - PRD (Product Requirements Document)

## 📋 Proje Özeti

Bu proje, Twitter'daki kullanıcı paylaşımlarını analiz ederek tematik ve duygusal içerik analizleri yapan web tabanlı bir uygulama geliştirilmesini amaçlamaktadır. Proje, konu modelleme (LDA), duygu analizi ve kelime bulutu analizi gibi doğal dil işleme tekniklerini birleştirerek kullanıcılara ileri düzey analitikler sunacaktır.

## 🎯 Proje Hedefleri

- **Veri Analizi**: Twitter arşivlerindeki tweet verilerini analiz etmek
- **Konu Modelleme**: LDA algoritması ile kullanıcıların ilgi alanlarını ortaya çıkarmak
- **Duygu Analizi**: Transformer tabanlı modeller ile duygusal eğilimleri belirlemek
- **Görselleştirme**: Kelime bulutları ve çeşitli grafiklerle sonuçları sunmak
- **Web Arayüzü**: Kullanıcı dostu, modern bir web arayüzü geliştirmek

## 🏗️ Sistem Mimarisi

### Mevcut Durumda Bulunan Bileşenler

1. **Analiz Modülleri** (`analiz/` klasörü):
   - `lda/lda_analizi.py` - Konu modelleme
   - `sentiment/duygu_analizi.py` - Duygu analizi
   - `wordcloud/wordcloud_olustur.py` - Kelime bulutu

2. **Veri Deposu** (`tweet_arsivleri/` klasörü):
   - JSON formatında tweet arşivleri
   - Kullanıcı bazlı ayrılmış veri dosyaları

### Yeni Geliştirilecek Bileşenler

1. **Backend API** (Flask/FastAPI)
2. **Frontend Web Arayüzü** (HTML/CSS/JavaScript)
3. **Veri İşleme Katmanı**
4. **Rapor Oluşturma Sistemi**

## 📑 Aşama Aşama Geliştirme Planı

### Aşama 1: Proje Yapısının Reorganizasyonu ve Altyapı Kurulumu

#### 1.1 Dosya Yapısının Düzenlenmesi
```
twitter_analiz_projesi/
├── app/
│   ├── __init__.py
│   ├── main.py (Flask uygulaması)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analiz_routes.py
│   │   └── api_routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handler.py
│   │   └── data_processor.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── analiz.html
│       └── sonuclar.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── analiz/
│   ├── __init__.py
│   ├── lda/
│   ├── sentiment/
│   └── wordcloud/
├── tweet_arsivleri/
├── sonuclar/
│   ├── lda_sonuclari/
│   ├── duygu_sonuclari/
│   └── wordcloud_sonuclari/
├── requirements.txt
├── config.py
└── run.py
```

#### 1.2 Bağımlılıkların Belirlenmesi
```python
# requirements.txt içeriği
Flask==2.3.3
pandas==2.0.3
numpy==1.24.3
gensim==4.3.2
pyLDAvis==3.4.1
transformers==4.33.2
torch==2.0.1
matplotlib==3.7.2
seaborn==0.12.2
wordcloud==1.9.2
scikit-learn==1.3.0
plotly==5.16.1
Jinja2==3.1.2
Werkzeug==2.3.6
tqdm==4.66.1
nltk==3.8.1
```

### Aşama 2: Backend API Geliştirmesi

#### 2.1 Flask Uygulaması Kurulumu
- Flask uygulamasının temel yapısını oluşturma
- Blueprint'lerle modüler yapı kurma
- Error handling ve logging mekanizmaları

#### 2.2 Veri İşleme API'leri
- Tweet arşivlerini listeleme endpoint'i
- Veri önizleme endpoint'i
- Analiz başlatma endpoint'i
- Analiz durumu sorgulama endpoint'i
- Sonuç getirme endpoint'i

#### 2.3 Analiz Modüllerinin Entegrasyonu
- Mevcut analiz fonksiyonlarını API'ye entegre etme
- Asenkron analiz işleme yapısı kurma
- Progress tracking sistemi

### Aşama 3: Frontend Web Arayüzü Geliştirmesi

#### 3.1 Modern UI/UX Tasarımı
- **Responsive Design**: Mobil ve desktop uyumlu
- **Material Design** veya **Bootstrap 5** kullanımı
- **Dark/Light Theme** desteği
- **Progress Indicators** ve **Loading States**

#### 3.2 Ana Sayfalar
1. **Dashboard/Ana Sayfa**:
   - Proje özeti
   - Hızlı başlangıç rehberi
   - Son analizler listesi

2. **Veri Seçimi Sayfası**:
   - Tweet arşivlerini listeleme
   - Dosya önizleme özelliği
   - Çoklu dosya seçimi
   - Veri filtreleme seçenekleri

3. **Analiz Konfigürasyonu Sayfası**:
   - Analiz türü seçimi (LDA, Duygu, Kelime Bulutu)
   - Parametre ayarları
   - İleri düzey seçenekler

4. **Sonuçlar Sayfası**:
   - İnteraktif görselleştirmeler
   - Indirilebilir raporlar
   - Sonuç paylaşım özellikleri

#### 3.3 JavaScript Özellikleri
- **AJAX** ile asenkron veri yükleme
- **Chart.js** veya **Plotly.js** ile interaktif grafikler
- **Real-time progress** tracking
- **Drag & Drop** dosya yükleme

### Aşama 4: Gelişmiş Analiz Özellikleri

#### 4.1 LDA Analizi Geliştirmeleri
```python
# Geliştirilmiş LDA parametreleri
- Optimal konu sayısı belirleme (Coherence Score)
- Interaktif konu görselleştirme
- Konu evrimi analizi (zaman bazlı)
- Konu benzerlik matrisi
```

#### 4.2 Duygu Analizi Geliştirmeleri
```python
# Çoklu model desteği
- BERT Türkçe modelleri
- XLM-RoBERTa çok dilli model
- Özel eğitilmiş modeller
- Ensemble metodları
```

#### 4.3 Kelime Bulutu Geliştirmeleri
```python
# İleri düzey özellikler
- Şekil bazlı kelime bulutları
- Renk tema seçenekleri
- Animasyonlu kelime bulutları
- Karşılaştırmalı kelime bulutları
```

### Aşama 5: Veri İşleme ve Ön İşleme

#### 5.1 Metin Ön İşleme Pipeline'ı
```python
class TextPreprocessor:
    def __init__(self):
        self.stopwords = set()
        self.stemmer = None
        
    def clean_text(self, text):
        # URL temizleme
        # Mention ve hashtag işleme
        # Emoji düzenleme
        # Noktalama işaretleri
        # Küçük harf dönüşümü
        pass
        
    def remove_stopwords(self, tokens):
        pass
        
    def stem_tokens(self, tokens):
        pass
```

#### 5.2 Veri Filtreleme ve Seçim
- Tarih aralığı filtresi
- Minimum/maksimum tweet uzunluğu
- Dil filtresi
- Kullanıcı aktivitesi bazlı filtreleme

### Aşama 6: Görselleştirme ve Raporlama

#### 6.1 İnteraktif Görselleştirmeler
1. **LDA Sonuçları**:
   - pyLDAvis entegrasyonu
   - Konu dağılım grafikleri
   - Zaman serisi konu analizi
   - Word-Topic probability matrisi

2. **Duygu Analizi**:
   - Duygu dağılım pastası
   - Zaman serisi duygu değişimi
   - Kelime bazlı duygu haritası
   - Karşılaştırmalı duygu grafikleri

3. **Kelime Bulutları**:
   - İnteraktif kelime bulutları
   - Konu bazlı kelime bulutları
   - Duygu bazlı renklendirme
   - Animasyonlu gösterimler

#### 6.2 Rapor Sistemi
```python
class ReportGenerator:
    def generate_pdf_report(self, analiz_sonuclari):
        # PDF rapor oluşturma
        pass
        
    def generate_excel_report(self, analiz_sonuclari):
        # Excel rapor oluşturma
        pass
        
    def generate_html_report(self, analiz_sonuclari):
        # HTML rapor oluşturma
        pass
```

### Aşama 7: Web Arayüzü İleri Düzey Özellikler

#### 7.1 Kullanıcı Deneyimi İyileştirmeleri
- **Otomatik Kaydetme**: Analiz parametrelerini otomatik kaydetme
- **Analiz Geçmişi**: Önceki analizleri görüntüleme ve karşılaştırma
- **Hızlı Analizler**: Önceden tanımlanmış analiz şablonları
- **Batch Processing**: Çoklu dosya analizi

#### 7.2 Paylaşım ve İşbirliği
- **URL Paylaşımı**: Analiz sonuçlarını URL ile paylaşma
- **Export Seçenekleri**: PNG, PDF, Excel formatlarında export
- **Sosyal Medya Entegrasyonu**: Sonuçları sosyal medyada paylaşma

#### 7.3 Performans Optimizasyonları
- **Caching**: Sık kullanılan analizleri cache'leme
- **Lazy Loading**: Büyük veri setleri için lazy loading
- **Progress Streaming**: Real-time analiz ilerlemesi
- **Memory Management**: Büyük dosyalar için memory optimization

### Aşama 8: Güvenlik ve Performans

#### 8.1 Güvenlik Önlemleri
- **Input Validation**: Kullanıcı girdilerini doğrulama
- **File Upload Security**: Güvenli dosya yükleme
- **Rate Limiting**: API kullanım limitleri
- **Error Handling**: Güvenli hata yönetimi

#### 8.2 Performans Optimizasyonları
- **Multiprocessing**: Paralel analiz işleme
- **Database Indexing**: Hızlı veri erişimi
- **CDN Integration**: Statik dosyalar için CDN
- **Compression**: Gzip kompresyon

## 🔧 Teknik Detaylar

### Veri Modeli
```python
class TwitterData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tweets = []
        self.user_info = {}
        self.date_range = None
        self.tweet_count = 0
        
class AnalysisResult:
    def __init__(self):
        self.lda_results = None
        self.sentiment_results = None
        self.wordcloud_path = None
        self.metadata = {}
        self.created_at = None
```

### API Endpoints
```python
# Veri Yönetimi
GET /api/files - Tweet dosyalarını listele
GET /api/files/{file_id}/preview - Dosya önizlemesi
POST /api/files/upload - Yeni dosya yükle

# Analiz İşlemleri
POST /api/analysis/start - Analiz başlat
GET /api/analysis/{analysis_id}/status - Analiz durumu
GET /api/analysis/{analysis_id}/results - Analiz sonuçları

# Sonuçlar
GET /api/results/{result_id} - Sonuç detayları
GET /api/results/{result_id}/download - Sonuç indir
```

## 🎨 UI/UX Tasarım Prensipleri

### 1. Kullanıcı Akışı
1. **Dosya Seçimi** → **Parametre Ayarları** → **Analiz Başlatma** → **Sonuç Görüntüleme**
2. **Hızlı Başlangıç** seçenekleri için kısayollar
3. **Step-by-step wizard** kullanıcı rehberliği

### 2. Görsel Tasarım
- **Modern, minimal tasarım**
- **Tutarlı renk paleti**
- **İkonografik gösterimler**
- **Responsive grid system**

### 3. Etkileşim Tasarımı
- **Hover effects** ve **smooth transitions**
- **Loading animations**
- **Toast notifications** için feedback
- **Keyboard shortcuts** power user'lar için

## 📊 Başarı Metrikleri

1. **Performans Metrikleri**:
   - Analiz süresi < 30 saniye (1000 tweet için)
   - Sayfa yükleme süresi < 3 saniye
   - Memory kullanımı < 512MB

2. **Kullanıcı Deneyimi**:
   - Intuitive navigation (user testing)
   - Error rate < %5
   - Mobile responsiveness %100

3. **Analiz Kalitesi**:
   - LDA coherence score > 0.4
   - Sentiment accuracy > %85
   - Meaningful word cloud generation

## 🚀 Gelecek Geliştirmeler

### Faz 2: AI Destekli Özellikler
- **Otomatik Insight Generation**: AI ile otomatik analiz özetleri
- **Anomaly Detection**: Olağandışı tweet patterns tespiti
- **Trend Prediction**: Gelecek trend tahminleri
- **Comparative Analysis**: Kullanıcılar arası karşılaştırma

### Faz 3: Sosyal Ağ Analizi
- **Network Graph**: Mention ve retweet ağları
- **Influence Analysis**: Etki analizi
- **Community Detection**: Topluluk tespiti
- **Viral Content Analysis**: Viral içerik analizi

### Faz 4: Real-time Özellikler
- **Live Twitter Integration**: Canlı Twitter API entegrasyonu
- **Real-time Dashboard**: Canlı analiz paneli
- **Alert System**: Trend değişimi uyarıları
- **Automated Reporting**: Otomatik periyodik raporlar

## 🔗 Entegrasyon Noktaları

### Harici API'ler
- **Twitter API v2**: Canlı veri çekimi için
- **Google Cloud Translation**: Çok dilli destek
- **AWS S3**: Büyük dosya depolama
- **Google Analytics**: Kullanım istatistikleri

### Database Seçenekleri
- **SQLite**: Geliştirme ortamı için
- **PostgreSQL**: Production ortamı için
- **Redis**: Caching için
- **MongoDB**: Document storage için

## 📝 Konfigürasyon Yönetimi

```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'
    
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = os.environ.get('DATABASE_URL')
```

Bu PRD dokümanı, Twitter analiz projesinin kapsamlı bir şekilde geliştirilmesi için gereken tüm aşamaları, teknolojileri ve özellikleri detaylandırmaktadır. Her aşama kendi içinde test edilebilir ve iterative olarak geliştirilebilir niteliktedir. 