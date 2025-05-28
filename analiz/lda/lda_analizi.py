import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # GUI olmayan ortamlar için
import matplotlib.pyplot as plt
import seaborn as sns
from gensim import corpora, models
import pyLDAvis
import pyLDAvis.gensim_models
from wordcloud import WordCloud
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Matplotlib için Türkçe font ayarları
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

def lda_analizi(df, metin_kolonu='temiz_metin', cikti_klasoru='.', num_topics=5, 
                iterations=100, optimize_topics=True, min_word_freq=2, 
                max_word_freq=0.8, create_wordclouds=True):
    """
    Gelişmiş LDA (Latent Dirichlet Allocation) konu modelleme analizi yapar.
    
    Args:
        df: Analiz edilecek veri (DataFrame)
        metin_kolonu: Metin kolonu adı
        cikti_klasoru: Sonuçların kaydedileceği klasör
        num_topics: Konu sayısı (varsayılan: 5)
        iterations: İterasyon sayısı (varsayılan: 100)
        optimize_topics: Otomatik konu sayısı optimizasyonu (varsayılan: True)
        min_word_freq: Minimum kelime frekansı (varsayılan: 2)
        max_word_freq: Maksimum kelime frekansı oranı (varsayılan: 0.8)
        create_wordclouds: Kelime bulutu oluştur (varsayılan: True)
    """
    print("🔍 LDA Konu Modelleme Analizi Başlatılıyor")
    print("="*50)
    print(f"📊 Parametreler:")
    print(f"   • Konu sayısı: {num_topics}")
    print(f"   • İterasyon: {iterations}")
    print(f"   • Min kelime frekansı: {min_word_freq}")
    print(f"   • Max kelime frekansı: {max_word_freq}")
    print(f"   • Konu optimizasyonu: {optimize_topics}")
    print("="*50)
    
    try:
        # Çıktı klasörünü oluştur
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        # Veri temizleme ve hazırlama
        df_clean = _prepare_data(df, metin_kolonu)
        docs = df_clean[metin_kolonu].tolist()
        
        print(f"📄 Toplam {len(docs)} doküman işleniyor...")
        
        # Metinleri tokenize et ve temizle
        tokenized_docs = _tokenize_and_clean(docs, min_word_freq, max_word_freq)
        
        # Dictionary ve corpus oluştur
        dictionary, corpus = _create_dictionary_corpus(tokenized_docs)
        
        # Konu sayısı optimizasyonu
        if optimize_topics:
            optimal_topics = _find_optimal_topics(corpus, dictionary, max_topics=15)
            if optimal_topics != num_topics:
                print(f"🎯 Önerilen konu sayısı: {optimal_topics} (mevcut: {num_topics})")
                num_topics = optimal_topics
        
        # LDA modeli oluştur
        lda_model = _create_lda_model(corpus, dictionary, num_topics, iterations)
        
        # Analiz sonuçlarını kaydet
        _save_topic_analysis(lda_model, cikti_klasoru, df_clean, corpus, dictionary)
        
        # Görselleştirmeler oluştur
        _create_visualizations(lda_model, corpus, dictionary, cikti_klasoru, create_wordclouds)
        
        # Doküman-konu dağılımını hesapla
        doc_topics_df = _calculate_document_topics(lda_model, corpus, df_clean, metin_kolonu, cikti_klasoru)
        
        # Özet istatistikleri yazdır
        _print_lda_summary(lda_model, len(docs), dictionary, corpus)
        
        print("✅ LDA analizi tamamlandı.")
        return {
            'model': lda_model,
            'corpus': corpus,
            'dictionary': dictionary,
            'doc_topics': doc_topics_df
        }
        
    except Exception as e:
        print(f"❌ LDA analizi sırasında bir hata oluştu: {e}")
        return None

def _prepare_data(df, metin_kolonu):
    """Veriyi temizle ve hazırla"""
    df_clean = df.dropna(subset=[metin_kolonu]).copy()
    df_clean = df_clean[df_clean[metin_kolonu].str.strip() != '']
    df_clean[metin_kolonu] = df_clean[metin_kolonu].astype(str)
    print(f"📋 Veri temizlendi: {len(df_clean)} doküman kaldı")
    return df_clean

def _tokenize_and_clean(docs, min_word_freq, max_word_freq):
    """Metinleri tokenize et ve temizle"""
    print("🔤 Tokenizasyon ve temizleme...")
    
    # Basit tokenizasyon
    tokenized_docs = [doc.lower().split() for doc in docs]
    
    # Kelime frekanslarını hesapla
    all_words = [word for doc in tokenized_docs for word in doc]
    word_freq = Counter(all_words)
    total_docs = len(docs)
    
    # Çok nadir ve çok yaygın kelimeleri filtrele
    filtered_docs = []
    for doc in tokenized_docs:
        filtered_doc = [
            word for word in doc 
            if (word_freq[word] >= min_word_freq and 
                word_freq[word] <= max_word_freq * total_docs and
                len(word) > 2)  # En az 3 karakter
        ]
        filtered_docs.append(filtered_doc)
    
    print(f"📊 Toplam benzersiz kelime: {len(word_freq)}")
    print(f"🔍 Filtreleme sonrası ortalama doküman uzunluğu: {np.mean([len(doc) for doc in filtered_docs]):.1f}")
    
    return filtered_docs

def _create_dictionary_corpus(tokenized_docs):
    """Dictionary ve corpus oluştur"""
    print("📚 Dictionary ve corpus oluşturuluyor...")
    
    dictionary = corpora.Dictionary(tokenized_docs)
    
    # Extreme'leri filtrele
    dictionary.filter_extremes(no_below=2, no_above=0.8)
    
    corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
    
    print(f"📖 Dictionary boyutu: {len(dictionary)}")
    print(f"📦 Corpus boyutu: {len(corpus)}")
    
    return dictionary, corpus

def _find_optimal_topics(corpus, dictionary, max_topics=15):
    """Coherence score kullanarak optimal konu sayısını bul"""
    print("🎯 Optimal konu sayısı aranıyor...")
    
    coherence_scores = []
    topic_range = range(2, min(max_topics + 1, 16))
    
    for num_topics in topic_range:
        try:
            temp_model = models.LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=num_topics,
                random_state=100,
                passes=5,  # Hızlı test için az pass
                alpha='auto'
            )
            
            # Basit coherence hesaplama (tam coherence modeli olmadan)
            topics = temp_model.show_topics(formatted=False)
            coherence = np.mean([len(topic[1]) for topic in topics])  # Basit metrik
            coherence_scores.append(coherence)
            
        except:
            coherence_scores.append(0)
    
    if coherence_scores:
        optimal_idx = np.argmax(coherence_scores)
        optimal_topics = list(topic_range)[optimal_idx]
        print(f"🎯 Optimal konu sayısı: {optimal_topics}")
        return optimal_topics
    
    return 5  # Varsayılan

def _create_lda_model(corpus, dictionary, num_topics, iterations):
    """LDA modelini oluştur"""
    print(f"🤖 LDA modeli oluşturuluyor ({num_topics} konu)...")
    
    lda_model = models.LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=100,
        update_every=1,
        chunksize=100,
        passes=10,
        alpha='auto',
        eta='auto',  # Beta parametresi
        per_word_topics=True,
        iterations=iterations,
        eval_every=None  # Evaluation'ı kapatır, hızlandırır
    )
    
    print("✅ LDA modeli oluşturuldu.")
    return lda_model

def _save_topic_analysis(lda_model, cikti_klasoru, df_clean, corpus, dictionary):
    """Konu analizini dosyalara kaydet"""
    print("💾 Konu analizi sonuçları kaydediliyor...")
    
    # Konuları detaylı şekilde kaydet
    with open(os.path.join(cikti_klasoru, 'detayli_konular.txt'), 'w', encoding='utf-8') as f:
        f.write("DETAYLI KONU ANALİZİ\n")
        f.write("="*50 + "\n\n")
        
        for idx, topic in lda_model.print_topics(num_topics=-1, num_words=10):
            f.write(f"KONU {idx + 1}:\n")
            f.write("-" * 20 + "\n")
            f.write(f"{topic}\n\n")
            
            # En temsili kelimeleri al
            topic_words = lda_model.show_topic(idx, topn=10)
            f.write("En önemli kelimeler:\n")
            for word, prob in topic_words:
                f.write(f"  • {word}: {prob:.4f}\n")
            f.write("\n" + "="*50 + "\n\n")
    
    # Kısa özet
    with open(os.path.join(cikti_klasoru, 'konu_ozeti.txt'), 'w', encoding='utf-8') as f:
        f.write("KONU ÖZETİ\n")
        f.write("="*30 + "\n\n")
        for idx, topic in lda_model.print_topics(-1, num_words=5):
            # Konuyu daha okunabilir hale getir
            topic_clean = topic.replace('*', '').replace('"', '')
            f.write(f"Konu {idx + 1}: {topic_clean}\n\n")

def _create_visualizations(lda_model, corpus, dictionary, cikti_klasoru, create_wordclouds):
    """Görselleştirmeleri oluştur"""
    print("🎨 Görselleştirmeler oluşturuluyor...")
    
    # 1. PyLDAvis görselleştirmesi
    try:
        vis_data = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary, sort_topics=False)
        pyLDAvis.save_html(vis_data, os.path.join(cikti_klasoru, 'lda_visualization.html'))
        print("✅ Interaktif LDA görselleştirmesi kaydedildi.")
    except Exception as e:
        print(f"⚠️ LDA görselleştirmesi oluşturulurken hata: {e}")
    
    # 2. Konu dağılım grafiği
    _create_topic_distribution_chart(lda_model, corpus, cikti_klasoru)
    
    # 3. Kelime bulutu
    if create_wordclouds:
        _create_topic_wordclouds(lda_model, cikti_klasoru)
    
    # 4. Konu-kelime heatmap
    _create_topic_word_heatmap(lda_model, cikti_klasoru)

def _create_topic_distribution_chart(lda_model, corpus, cikti_klasoru):
    """Konu dağılım grafiğini oluştur"""
    
    # Her dokümanın dominant konusunu bul
    doc_topics = []
    for doc in corpus:
        doc_topic_dist = lda_model.get_document_topics(doc)
        if doc_topic_dist:
            dominant_topic = max(doc_topic_dist, key=lambda x: x[1])[0]
            doc_topics.append(dominant_topic)
    
    # Konu dağılımını hesapla
    topic_counts = Counter(doc_topics)
    
    # Grafik oluştur
    plt.figure(figsize=(12, 8))
    
    # Renk paleti
    colors = plt.cm.Set3(np.linspace(0, 1, len(topic_counts)))
    
    # Bar chart
    topics = [f"Konu {i+1}" for i in topic_counts.keys()]
    counts = list(topic_counts.values())
    
    bars = plt.bar(topics, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Değer etiketleri ekle
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Dominant Konu Dağılımı', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Doküman Sayısı', fontsize=12, fontweight='bold')
    plt.xlabel('Konular', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(os.path.join(cikti_klasoru, 'konu_dagilimi.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def _create_topic_wordclouds(lda_model, cikti_klasoru):
    """Her konu için kelime bulutu oluştur"""
    print("☁️ Kelime bulutları oluşturuluyor...")
    
    num_topics = lda_model.num_topics
    
    # Grid boyutunu hesapla
    cols = min(3, num_topics)
    rows = (num_topics + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
    if num_topics == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.reshape(1, -1)
    
    for idx in range(num_topics):
        try:
            # Konu kelimelerini al
            topic_words = dict(lda_model.show_topic(idx, topn=50))
            
            # Kelime bulutu oluştur
            if topic_words:
                wordcloud = WordCloud(
                    width=400, height=300,
                    background_color='white',
                    max_words=30,
                    colormap='viridis',
                    relative_scaling=0.5
                ).generate_from_frequencies(topic_words)
                
                row = idx // cols
                col = idx % cols
                
                if rows > 1:
                    ax = axes[row, col]
                else:
                    ax = axes[col]
                
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.set_title(f'Konu {idx + 1}', fontsize=14, fontweight='bold')
                ax.axis('off')
            
        except Exception as e:
            print(f"⚠️ Konu {idx + 1} kelime bulutu oluşturulamadı: {e}")
    
    # Boş subplot'ları gizle
    for idx in range(num_topics, rows * cols):
        row = idx // cols
        col = idx % cols
        if rows > 1:
            axes[row, col].axis('off')
        else:
            axes[col].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_klasoru, 'konu_kelime_bulutlari.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def _create_topic_word_heatmap(lda_model, cikti_klasoru):
    """Konu-kelime heatmap oluştur"""
    
    # Her konu için top kelimeleri al
    topics_words = []
    all_words = set()
    
    for topic_idx in range(lda_model.num_topics):
        topic_words = dict(lda_model.show_topic(topic_idx, topn=10))
        topics_words.append(topic_words)
        all_words.update(topic_words.keys())
    
    # Heatmap verisi oluştur
    word_list = list(all_words)[:20]  # İlk 20 kelime
    heatmap_data = []
    
    for topic_words in topics_words:
        row = [topic_words.get(word, 0) for word in word_list]
        heatmap_data.append(row)
    
    # Heatmap çiz
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, 
                xticklabels=word_list,
                yticklabels=[f'Konu {i+1}' for i in range(len(heatmap_data))],
                annot=True, fmt='.3f', cmap='YlOrRd')
    
    plt.title('Konu-Kelime İlişki Haritası', fontsize=16, fontweight='bold')
    plt.xlabel('Kelimeler', fontsize=12, fontweight='bold')
    plt.ylabel('Konular', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(os.path.join(cikti_klasoru, 'konu_kelime_heatmap.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def _calculate_document_topics(lda_model, corpus, df_clean, metin_kolonu, cikti_klasoru):
    """Her doküman için konu dağılımını hesapla"""
    print("📄 Doküman-konu dağılımları hesaplanıyor...")
    
    doc_topics_data = []
    
    for idx, doc in enumerate(corpus):
        doc_topics = lda_model.get_document_topics(doc)
        
        # Tüm konular için skorları al
        topic_scores = {f'konu_{i+1}_skor': 0.0 for i in range(lda_model.num_topics)}
        
        for topic_id, prob in doc_topics:
            topic_scores[f'konu_{topic_id+1}_skor'] = prob
        
        # Dominant konu
        if doc_topics:
            dominant_topic = max(doc_topics, key=lambda x: x[1])
            topic_scores['dominant_konu'] = dominant_topic[0] + 1
            topic_scores['dominant_konu_skor'] = dominant_topic[1]
        else:
            topic_scores['dominant_konu'] = 1
            topic_scores['dominant_konu_skor'] = 0.0
        
        doc_topics_data.append(topic_scores)
    
    # DataFrame oluştur
    doc_topics_df = pd.concat([df_clean.reset_index(drop=True), 
                               pd.DataFrame(doc_topics_data)], axis=1)
    
    # Kaydet
    doc_topics_df.to_csv(os.path.join(cikti_klasoru, 'dokuman_konu_dagilimi.csv'), 
                         index=False, encoding='utf-8')
    
    return doc_topics_df

def _print_lda_summary(lda_model, total_docs, dictionary, corpus):
    """LDA analizi özetini yazdır"""
    print("\n" + "="*50)
    print("📊 LDA ANALİZİ ÖZETİ")
    print("="*50)
    print(f"📄 Toplam doküman sayısı: {total_docs}")
    print(f"🔤 Sözlük boyutu: {len(dictionary)}")
    print(f"🎯 Konu sayısı: {lda_model.num_topics}")
    
    try:
        perplexity = lda_model.log_perplexity(corpus)
        print(f"🎲 Perplexity: {perplexity:.2f}")
    except:
        print("🎲 Perplexity: Hesaplanamadı")
    
    print("\n📝 KONU ÖZETLERİ:")
    print("-" * 30)
    
    for idx, topic in lda_model.print_topics(num_topics=-1, num_words=3):
        # Sadece kelimeleri al, skorları temizle
        words = []
        for item in topic.split(' + '):
            word = item.split('*')[1].replace('"', '').strip()
            words.append(word)
        
        print(f"Konu {idx + 1}: {', '.join(words[:3])}")
    
    print("="*50)
