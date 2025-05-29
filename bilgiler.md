# Twitter Veri Çekimi ve Analiz Sistemi - Teknik Bilgiler

## 🎯 Proje Özeti
Bu proje, Twitter'dan kullanıcı tweet'lerini çekme, temizleme ve analiz etme amacıyla geliştirilmiş kapsamlı bir sistemdir. Twikit kütüphanesi ile Twitter API erişimi, Flask ile web arayüzü ve çeşitli NLP teknikleri kullanılmıştır.

---

## 🏗️ Sistem Mimarisi

### 1. **Modüler Yapı**
```
proje/
├── twikit_sandbox/          # Twitter veri çekme modülü
│   └── tweet_fetcher.py     # Ana veri çekme scripti
├── app/                     # Flask web uygulaması
│   ├── routes/             # URL route'ları
│   ├── templates/          # HTML şablonları
│   └── utils/              # Yardımcı fonksiyonlar
├── analiz/                  # Analiz modülleri
│   ├── preprocessing.py     # Veri ön işleme
│   ├── sentiment/          # Sentiment analizi
│   ├── wordcloud/          # Kelime bulutu
│   └── lda/                # Konu modelleme
└── static/                  # CSS, JS dosyaları
```

### 2. **Veri Akış Şeması**
```
Twitter API → Veri Çekme → Ön İşleme → Analiz → Görselleştirme → Web Arayüzü
```

---

## 🔧 Teknoloji Stack'i

### **Backend Teknolojileri**
- **Python 3.9+**: Ana programlama dili
- **Flask 3.0.0**: Web framework
- **Twikit 1.7.4**: Twitter API wrapper
- **AsyncIO**: Asenkron programlama

### **Veri İşleme Kütüphaneleri**
- **Pandas 2.1.4**: Veri manipülasyonu
- **NumPy**: Sayısal hesaplamalar
- **JSON**: Veri saklama formatı

### **NLP (Doğal Dil İşleme) Kütüphaneleri**
- **NLTK 3.8.1**: Tokenization, stop words
- **TextBlob 0.17.1**: Sentiment analizi
- **scikit-learn 1.3.2**: TF-IDF, clustering
- **WordCloud 1.9.2**: Kelime bulutu oluşturma

---

## 📊 Veri Ön İşleme (Preprocessing)

### **1. Metin Temizleme Adımları**

#### **URL Temizleme**
```python
import re
text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
```

#### **Mention ve Hashtag Temizleme**
```python
text = re.sub(r'@\w+|#\w+', '', text)
```

#### **Özel Karakter Filtreleme**
```python
text = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ\s]', '', text)
```

### **2. Tokenization (Kelime Ayırma)**
```python
from nltk.tokenize import word_tokenize
tokens = word_tokenize(text.lower())
```

### **3. Stop Word Removal (Gereksiz Kelime Çıkarma)**
```python
from nltk.corpus import stopwords
turkish_stopwords = stopwords.words('turkish')
filtered_tokens = [word for word in tokens if word not in turkish_stopwords]
```

### **4. Normalizasyon**
- Büyük/küçük harf dönüşümü
- Boşluk karakterlerinin düzenlenmesi
- Türkçe karakter desteği

---

## 🤖 Analiz Teknikleri

### **1. Sentiment Analizi**

#### **TextBlob Kullanımı**
```python
from textblob import TextBlob
sentiment = TextBlob(text).sentiment.polarity
# -1 (negatif) ile +1 (pozitif) arası değer döner
```

#### **Sentiment Kategorileri**
- **Pozitif**: 0.1 ≤ polarity ≤ 1.0
- **Nötr**: -0.1 < polarity < 0.1  
- **Negatif**: -1.0 ≤ polarity ≤ -0.1

### **2. TF-IDF (Term Frequency-Inverse Document Frequency)**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1,2))
tfidf_matrix = vectorizer.fit_transform(documents)
```

#### **TF-IDF Formülü**
```
TF-IDF(t,d) = TF(t,d) × IDF(t)
TF(t,d) = (Kelime sayısı) / (Toplam kelime sayısı)
IDF(t) = log(Toplam doküman / Kelimeyi içeren doküman)
```

### **3. LDA (Latent Dirichlet Allocation) Konu Modelleme**
```python
from sklearn.decomposition import LatentDirichletAllocation
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(tfidf_matrix)
```

#### **LDA Nasıl Çalışır?**
- Her dokümana olasılıksal konu dağılımı atar
- Her konuya kelime dağılımı atar
- Iteratif algoritma ile optimize eder

---

## 🌐 Web Arayüzü (Flask)

### **Route Yapısı**
```python
from flask import Flask, render_template, request

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Analiz işlemleri
    return render_template('results.html')
```

### **Template Sistemi**
- **Jinja2 Template Engine** kullanımı
- **Bootstrap** ile responsive tasarım
- **AJAX** ile asenkron işlemler

---

## 🔐 Twitter API Entegrasyonu

### **Twikit Kütüphanesi**
```python
from twikit import Client
client = Client(language='tr-TR')

# Giriş yapma
await client.login(
    auth_info_1=username,
    auth_info_2=email, 
    password=password
)
```

### **Cookie Yönetimi**
```python
# Cookie kaydetme
client.save_cookies('twikit_cookies.json')

# Cookie yükleme
client.load_cookies('twikit_cookies.json')
```

### **Sayfalandırma (Pagination)**
```python
tweets = await user.get_tweets('Tweets', count=200)
while tweets:
    # Tweet'leri işle
    tweets = await tweets.next()  # Sonraki sayfa
```

---

## 📈 Analiz Sonuçları ve Görselleştirme

### **1. Kelime Bulutu (WordCloud)**
```python
from wordcloud import WordCloud
wordcloud = WordCloud(
    width=800, height=400,
    background_color='white',
    max_words=100,
    font_path='fonts/turkish_font.ttf'  # Türkçe karakter desteği
).generate(text)
```

### **2. İstatistiksel Analizler**
- **Tweet sayısı dağılımı**
- **Sentiment dağılımı** (pozitif/negatif/nötr)
- **En sık kullanılan kelimeler**
- **Konu dağılımları**

---

## ⚡ Performans Optimizasyonu

### **1. Asenkron Programlama**
```python
import asyncio
async def fetch_tweets():
    # Asenkron tweet çekme
    pass

# Birden fazla işlemi paralel çalıştırma
await asyncio.gather(task1, task2, task3)
```

### **2. Memory Management**
- **Batch Processing**: Büyük verileri parça parça işleme
- **Generator kullanımı**: Memory efficient iteration
- **Garbage Collection**: Gereksiz nesneleri temizleme

### **3. Caching Stratejileri**
- **Cookie tabanlı oturum** - Twitter login
- **File caching** - İşlenmiş veriler
- **In-memory caching** - Sık kullanılan sonuçlar

---

## 🛡️ Hata Yönetimi ve Güvenlik

### **1. Exception Handling**
```python
try:
    tweets = await client.get_tweets()
except Exception as e:
    if "authenticate" in str(e).lower():
        # Cookie'leri temizle, yeniden giriş yap
        os.remove(cookie_file)
    logger.error(f"Hata: {e}")
```

### **2. Rate Limiting**
- Twitter API sınırlarına uyum
- Bekleme mekanizmaları
- Otomatik retry logic

### **3. Güvenlik Önlemleri**
- Hassas bilgilerin environment variable'larda tutulması
- Input validation
- XSS koruması

---

## 🧪 Test Senaryoları

### **1. Birim Testleri**
- Ön işleme fonksiyonları
- Sentiment analiz doğruluğu
- API bağlantı testleri

### **2. Entegrasyon Testleri**
- End-to-end veri akışı
- Web arayüzü fonksiyonalitesi
- Farklı kullanıcı hesapları ile test

---

## 📚 Kullanılan Algoritmalar

### **1. Text Preprocessing Pipeline**
1. **Cleaning** → 2. **Tokenization** → 3. **Normalization** → 4. **Filtering**

### **2. Machine Learning Algorithms**
- **Naive Bayes** (Sentiment classification)
- **K-Means** (Tweet clustering)  
- **LDA** (Topic modeling)
- **TF-IDF** (Feature extraction)

### **3. Statistical Methods**
- **Frequency Analysis** (Kelime sıklığı)
- **Correlation Analysis** (Değişken ilişkileri)
- **Distribution Analysis** (Veri dağılımları)

---

## 🎤 Sunu İçin Önemli Noktalar

### **Teknik Sorulara Hazırlık**

#### **"Neden Twikit kullandınız?"**
- Resmi Twitter API'ye göre daha az kısıtlama
- Python-friendly interface
- Asenkron işlem desteği
- Cookie-based session management

#### **"Sentiment analizi nasıl çalışıyor?"**
- TextBlob kütüphanesi pre-trained model kullanıyor
- -1 ile +1 arası polarity skoru hesaplıyor
- Türkçe dil desteği mevcut
- Doğruluk oranı yaklaşık %75-80

#### **"LDA algoritması nedir?"**
- Unsupervised learning algoritması
- Dokümanları gizli konulara ayırır
- Probabilistic model (olasılıksal)
- Dirichlet dağılımı kullanır

#### **"Ön işleme neden gerekli?"**
- Noise'u (gürültü) azaltır
- Model performansını artırır
- Standardization sağlar
- Memory kullanımını optimize eder

#### **"Flask neden seçildi?"**
- Lightweight ve flexible
- Python ecosystem'ine uyumlu
- Rapid prototyping için ideal
- Jinja2 template engine

---

## 🔍 Olası Geliştirmeler

### **Kısa Vadeli**
- Real-time tweet streaming
- More sophisticated sentiment models
- User interface improvements
- Mobile responsive design

### **Uzun Vadeli**
- Deep learning models (BERT, GPT)
- Multi-language support
- Big data processing (Spark)
- Machine learning pipeline automation

---

## 📖 Referans Kaynaklar

### **Temel Kaynaklar**
- [Twikit Documentation](https://github.com/d60/twikit)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [NLTK Book](https://www.nltk.org/book/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

### **Akademik Kaynaklar**
- Sentiment Analysis research papers
- Topic Modeling (LDA) papers
- Social Media Analytics studies
- Turkish NLP resources

---

## ⚠️ Önemli Notlar

### **Lisans ve Etik**
- Twitter Terms of Service'e uyum
- Veri privacy considerations
- Academic use için uygun
- Commercial use için lisans gerekebilir

### **Teknik Limitasyonlar**
- Twitter API rate limits
- Memory constraints for large datasets
- Processing time for complex analyses
- Internet connection dependency 