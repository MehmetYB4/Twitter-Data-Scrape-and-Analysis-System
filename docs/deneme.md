graph LR
    subgraph "Kullanıcı Arayüzü/API"
        A[Kullanıcı Analiz Başlatır<br>(/analiz/baslat POST)]
    end

    subgraph "app/routes/analiz_routes.py"
        B(analiz_baslat)
        C(analiz_hizli_calistir)
    end

    subgraph "analiz/ (Bağımsız Analiz Modülleri)"
        D(lda_analizi.py<br>lda_analizi())
        E(duygu_analizi.py<br>duygu_analizi())
        F(wordcloud_olustur.py<br>wordcloud_olustur())
    end

    subgraph "Dosya Sistemi"
        G[/sonuclar/{analiz_klasoru_adi}/]
        H[/sonuclar/{analiz_klasoru_adi}/lda/]
        I[/sonuclar/{analiz_klasoru_adi}/sentiment/]
        J[/sonuclar/{analiz_klasoru_adi}/wordcloud/]
    end

    A --> B
    B -- Async/Sync Çağrı --> C

    C -- Veri Yükler & Hazırlar --> C
    C -- Sonuç Klasörü Oluşturur --> G

    C -- Eğer 'lda' seçili --> D
    D -- LDA Sonuçlarını Kaydeder --> H

    C -- Eğer 'sentiment' seçili --> E
    E -- Duygu Analizi Sonuçlarını Kaydeder --> I

    C -- Eğer 'wordcloud' seçili --> F
    F -- Kelime Bulutu Sonuçlarını Kaydeder --> J

    C -- Analiz Durumunu Günceller --> B