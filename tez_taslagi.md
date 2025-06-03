# Twitter Veri Çekimi ve Analiz Sistemi: `twikit`, Flask ve Doğal Dil İşleme Uygulaması

## Özet (Abstract)
*   Projenin amacı ve kapsamı
*   Kullanılan temel teknolojiler (Python, Flask, `twikit`, NLP kütüphaneleri)
*   Elde edilen temel sonuçlar ve sistemin yetenekleri

## 1. Giriş
    1.1. Problem Tanımı ve Motivasyon
        *   Sosyal medya verilerinin önemi
        *   Twitter verilerinin analiz ihtiyacı
    1.2. Projenin Amacı ve Kapsamı
        *   Belirli kullanıcıların tweetlerini çekme
        *   Veri ön işleme ve temizleme
        *   Duygu analizi, kelime bulutu, konu modelleme gibi NLP analizleri
        *   Sonuçların web arayüzü üzerinden sunulması
    1.3. Tezin Yapısı

## 2. İlgili Çalışmalar (Literatür Taraması)
    2.1. Twitter Veri Toplama Yöntemleri
        *   Twitter API ve kısıtlamaları
        *   Alternatif kütüphaneler (`twikit` gibi)
    2.2. Doğal Dil İşleme Teknikleri
        *   Metin ön işleme
        *   Duygu analizi yaklaşımları
        *   Kelime bulutu oluşturma
        *   Konu modelleme (LDA)
    2.3. Web Tabanlı Veri Analiz Platformları

## 3. Sistem Mimarisi ve Tasarımı
    3.1. Genel Sistem Mimarisi (Diyagram ile desteklenebilir)
        *   Veri toplama modülü
        *   Veri depolama
        *   Analiz motoru
        *   Web arayüzü (Flask uygulaması)
    3.2. Kullanılan Teknolojiler ve Kütüphaneler
        *   Programlama Dili: Python
        *   Web Framework: Flask
        *   Veri Çekme: `twikit`
        *   NLP Kütüphaneleri: `NLTK`, `TextBlob`, `wordcloud`, `gensim`/`scikit-learn` (README'ye göre)
        *   Veritabanı: SQLite (yapılandırmaya göre)
    3.3. Modül Bazlı Tasarım
        *   `app` (Flask uygulaması): `routes`, `templates`
        *   `analiz` (Analiz modülleri): `preprocessing`, `sentiment`, `wordcloud`, `lda`
        *   `twikit_sandbox` (Veri çekme scripti)
    3.4. Veri Akışı

## 4. Uygulama Geliştirme
    4.1. Veri Toplama (`tweet_fetcher.py`)
        *   `twikit` kütüphanesi ile Twitter'a erişim.
        *   Asenkron programlama (`asyncio`) ile verimli veri çekimi.
        *   Kullanıcıdan hedef hesap adı ve tweet sayısı alma.
        *   Cookie tabanlı oturum yönetimi (`twikit_cookies.json`):
            *   Mevcut cookie varsa kullanma.
            *   Yoksa kullanıcı adı, e-posta, şifre ile giriş yapıp cookie kaydetme.
            *   Kimlik doğrulama hatalarında cookie dosyasını silme.
        *   Belirtilen sayıda tweet çekilene kadar veya kullanıcının tüm tweetleri bitene kadar sayfalama (pagination) ile veri toplama.
        *   Çekilen tweet metinlerinin JSON formatında (`{kullanici_adi}_tweets.json`) kaydedilmesi.
        *   Hata yönetimi ve oturum kapatma.
    4.2. Veri Ön İşleme (`analiz/preprocessing.py`)
        *   Kapsamlı Türkçe stopword listesi (`TURKISH_STOPWORDS`).
        *   Regex tabanlı temizleme fonksiyonları:
            *   URL, HTML etiketleri, @bahsetmeler, #hashtag'ler.
            *   E-posta adresleri, telefon numaraları, sayılar.
            *   Emoji ve özel karakterler, noktalama işaretleri.
        *   Normalizasyon:
            *   Türkçe karakterlerin ASCII karşılıklarına dönüştürülmesi (`normalize_turkish_chars`).
            *   Unicode normalizasyonu (`normalize_unicode`).
            *   Küçük harfe çevirme.
        *   Metin iyileştirme:
            *   Fazla boşlukların kaldırılması.
            *   Tekrarlanan karakterlerin sınırlandırılması (`remove_repeated_chars`).
        *   Kelime bazlı filtreleme:
            *   Belirli bir uzunluk aralığındaki kelimeleri tutma (`filter_by_length`).
            *   Stopword'leri kaldırma (`remove_stopwords`), özel stopword ekleme imkanı.
            *   Belirli bir frekans aralığındaki kelimeleri tutma (`filter_by_frequency`).
        *   Pipeline'lar:
            *   `basic_preprocess`: Temel metin temizleme adımlarını uygular.
            *   `advanced_preprocess`: Temel temizlik sonrası kelime bazlı gelişmiş işlemler yapar.
            *   Analiz türlerine özel ön işleme fonksiyonları: `preprocess_for_lda`, `preprocess_for_sentiment`, `preprocess_for_wordcloud`.
            *   Toplu ön işleme için `batch_preprocess`.
    4.3. Analiz Modülleri
        *   4.3.1. Duygu Analizi (`analiz/sentiment/duygu_analizi.py`)
            *   `transformers` kütüphanesi ve `savasy/bert-base-turkish-sentiment-cased` modeli kullanımı.
            *   Metinleri batch'ler halinde işleme, GPU desteği (varsa).
            *   Her metin için pozitif, negatif, nötr skorlarının elde edilmesi.
            *   Nötr sınıfı için ayarlanabilir güven eşiği (`neutral_threshold`).
            *   Sonuçların (etiket ve skor) ana DataFrame'e eklenmesi.
            *   Detaylı skorların (pozitif, negatif, nötr) ayrı kolonlar olarak eklenmesi.
            *   Görselleştirme (`_create_professional_charts`):
                *   Matplotlib ve Seaborn kullanılarak profesyonel grafikler.
                *   Tweet duygu dağılımı için bar ve pie chart.
                *   Pozitif, negatif, nötr ve genel güven skorları için histogramlar.
                *   Grafiklerin PNG formatında kaydedilmesi.
            *   Sonuçların CSV dosyasına (`duygu_analizi_sonuclari.csv`) kaydedilmesi.
            *   Özet istatistiklerin konsola yazdırılması (`_print_summary_stats`).
        *   4.3.2. Kelime Bulutu Oluşturma (`analiz/wordcloud/wordcloud_olustur.py`)
            *   `wordcloud` kütüphanesi kullanımı.
            *   Metin verisinin ön işlenmesi (`_process_text`):
                *   Küçük harfe çevirme, sayıların ve noktalama işaretlerinin kaldırılması.
                *   Minimum kelime uzunluğu filtresi.
                *   Dahili Türkçe stopword listesi ve özel stopword ekleme imkanı.
            *   Kelime frekanslarının hesaplanması (`collections.Counter`).
            *   Ana kelime bulutunun oluşturulması ve kaydedilmesi (`_create_main_wordcloud`, `ana_kelime_bulutu.png`):
                *   Ayarlanabilir maksimum kelime sayısı, renk şeması.
                *   Özel şekil maskesi (`shape_mask` ile PIL/Pillow kullanılarak) uygulama seçeneği.
            *   İsteğe bağlı olarak farklı renk şemalarıyla çoklu kelime bulutları oluşturma (`_create_multiple_wordclouds`).
            *   Kelime frekans istatistiklerinin CSV dosyasına kaydedilmesi (`_create_word_statistics`, `kelime_istatistikleri.csv`).
            *   Özet bilgilerin konsola yazdırılması (`_print_wordcloud_summary`).
        *   4.3.3. LDA Konu Modelleme (`analiz/lda/lda_analizi.py`)
            *   `gensim` kütüphanesi ile Latent Dirichlet Allocation uygulaması.
            *   Veri hazırlama (`_prepare_data`) ve metinlerin tokenizasyonu/temizlenmesi (`_tokenize_and_clean`):
                *   Minimum ve maksimum kelime frekansı filtreleri.
            *   `gensim.corpora.Dictionary` ve BoW (Bag-of-Words) corpus oluşturma (`_create_dictionary_corpus`).
            *   İsteğe bağlı olarak optimal konu sayısının coherence skoru ile belirlenmesi (`_find_optimal_topics`).
            *   LDA modelinin oluşturulması (`_create_lda_model`):
                *   Ayarlanabilir konu sayısı, iterasyon sayısı.
            *   Analiz sonuçlarının kaydedilmesi:
                *   Detaylı konu başlıkları ve her konu için en önemli kelimelerin metin dosyalarına kaydedilmesi (`_save_topic_analysis`, `detayli_konular.txt`, `konu_ozeti.txt`).
            *   Görselleştirmeler (`_create_visualizations`):
                *   `pyLDAvis.gensim_models` ile interaktif LDA görselleştirmesi (HTML dosyası olarak kaydedilir: `lda_visualization.html`).
                *   Konu dağılım grafiği (`_create_topic_distribution_chart`).
                *   İsteğe bağlı olarak her konu için kelime bulutları (`_create_topic_wordclouds`) ve konu-kelime ısı haritası (`_create_topic_word_heatmap`).
            *   Her dokümanın hangi konulara ait olduğunun olasılık dağılımının hesaplanması ve CSV'ye kaydedilmesi (`_calculate_document_topics`).
            *   LDA model özet istatistiklerinin konsola yazdırılması (`_print_lda_summary`).
    4.4. Web Arayüzü (Flask Uygulaması - `app` klasörü, `run.py`)
        *   Route tanımları (`app/routes/`)
        *   HTML şablonları (`app/templates/`)
        *   Statik dosyalar (`static/`)
        *   Kullanıcı arayüzü ile analiz tetikleme ve sonuç görüntüleme
    4.5. Yapılandırma Yönetimi (`config.py`)
        *   Farklı ortamlar için yapılandırma (geliştirme, üretim)
        *   Hassas verilerin yönetimi (API anahtarları, şifreler - README'deki uyarı dikkate alınarak)

## 5. Test ve Değerlendirme
    5.1. Test Senaryoları
        *   Veri çekme doğruluğu
        *   Analiz modüllerinin işlevselliği
        *   Web arayüzü kullanılabilirliği
    5.2. Performans Değerlendirmesi (Opsiyonel, yapılabilirse)
        *   Veri çekme hızı
        *   Analiz süreleri
    5.3. Karşılaşılan Zorluklar ve Çözümler

## 6. Sonuç ve Gelecek Çalışmalar
    6.1. Projenin Özeti ve Elde Edilen Başarılar
    6.2. Sistemin Kısıtlılıkları
    6.3. Gelecekte Yapılabilecek İyileştirmeler ve Eklemeler
        *   Daha gelişmiş NLP modelleri entegrasyonu
        *   Gerçek zamanlı analiz yetenekleri
        *   Kullanıcı yönetimi ve kişiselleştirme
        *   Daha kapsamlı görselleştirmeler

## Referanslar
*   Kullanılan kütüphanelerin dokümantasyonları
*   İlgili akademik makaleler ve kaynaklar

## Ekler (Opsiyonel)
*   Önemli kod parçacıkları
*   Arayüz ekran görüntüleri 