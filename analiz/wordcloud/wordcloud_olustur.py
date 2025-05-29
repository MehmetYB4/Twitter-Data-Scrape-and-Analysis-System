import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI olmayan ortamlar için
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from collections import Counter
from PIL import Image, ImageDraw
import warnings
warnings.filterwarnings('ignore')

# Matplotlib için Türkçe font ayarları
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

def wordcloud_olustur(df, metin_kolonu='temiz_metin', cikti_klasoru='.', max_words=200, 
                      color_scheme='viridis', create_multiple=True, min_word_length=3,
                      remove_numbers=True, custom_stopwords=None, shape_mask=None,
                      create_stats=True):
    """
    Gelişmiş kelime bulutu oluşturur ve analiz yapar.
    
    Args:
        df: Analiz edilecek veri (DataFrame)
        metin_kolonu: Metin kolonu adı
        cikti_klasoru: Sonuçların kaydedileceği klasör
        max_words: Maksimum kelime sayısı (varsayılan: 200)
        color_scheme: Renk şeması (viridis, plasma, Set1, Set2, vb.)
        create_multiple: Çoklu görselleştirme oluştur (varsayılan: True)
        min_word_length: Minimum kelime uzunluğu (varsayılan: 3)
        remove_numbers: Sayıları kaldır (varsayılan: True)
        custom_stopwords: Özel stopword listesi
        shape_mask: Özel şekil maskesi dosya yolu
        create_stats: Kelime istatistikleri oluştur (varsayılan: True)
    """
    print("☁️ Gelişmiş Kelime Bulutu Analizi Başlatılıyor")
    print("="*55)
    print(f"📊 Parametreler:")
    print(f"   • Maksimum kelime: {max_words}")
    print(f"   • Renk şeması: {color_scheme}")
    print(f"   • Minimum kelime uzunluğu: {min_word_length}")
    print(f"   • Sayıları kaldır: {remove_numbers}")
    print(f"   • Çoklu görselleştirme: {create_multiple}")
    print("="*55)
    
    try:
        # Çıktı klasörünü oluştur
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        # Veriyi temizle ve hazırla
        df_clean = _prepare_wordcloud_data(df, metin_kolonu)
        
        # Metni işle ve temizle
        processed_text, word_freq = _process_text(
            df_clean, metin_kolonu, min_word_length, remove_numbers, custom_stopwords
        )
        
        if not processed_text:
            print("❌ İşlenecek metin bulunamadı!")
            return False
        
        # Şekil maskesi yükle (varsa)
        mask_array = _load_shape_mask(shape_mask) if shape_mask else None
        
        # Ana kelime bulutunu oluştur
        _create_main_wordcloud(processed_text, cikti_klasoru, max_words, 
                              color_scheme, mask_array)
        
        # Çoklu görselleştirmeler
        if create_multiple:
            _create_multiple_wordclouds(processed_text, word_freq, cikti_klasoru, max_words)
        
        # İstatistikleri oluştur
        if create_stats:
            _create_word_statistics(word_freq, df_clean, metin_kolonu, cikti_klasoru)
        
        # Özet bilgileri yazdır
        _print_wordcloud_summary(word_freq, len(df_clean))
        
        print("✅ Kelime bulutu analizi tamamlandı.")
        
        # Analiz sonuçlarını return et
        return {
            'word_frequencies': dict(word_freq.most_common(50)),  # En sık kullanılan 50 kelime
            'summary': {
                'total_texts': len(df_clean),
                'unique_words': len(word_freq),
                'total_words': sum(word_freq.values()),
                'most_common_word': word_freq.most_common(1)[0] if word_freq else None
            },
            'output_folder': cikti_klasoru,
            'files_created': ['ana_kelime_bulutu.png', 'kelime_istatistikleri.csv']
        }
        
    except Exception as e:
        print(f'❌ Kelime bulutu oluşturulurken hata: {e}')
        return None

def _prepare_wordcloud_data(df, metin_kolonu):
    """Veriyi kelime bulutu için temizle"""
    df_clean = df.dropna(subset=[metin_kolonu]).copy()
    df_clean = df_clean[df_clean[metin_kolonu].str.strip() != '']
    df_clean[metin_kolonu] = df_clean[metin_kolonu].astype(str)
    print(f"📋 Veri temizlendi: {len(df_clean)} metin kaldı")
    return df_clean

def _process_text(df_clean, metin_kolonu, min_word_length, remove_numbers, custom_stopwords):
    """Metni işle ve kelime frekanslarını hesapla"""
    print("🔤 Metin işleniyor ve temizleniyor...")
    
    # Tüm metni birleştir
    all_text = ' '.join(df_clean[metin_kolonu])
    
    # Temel temizlik
    all_text = all_text.lower()
    
    # Sayıları kaldır
    if remove_numbers:
        import re
        all_text = re.sub(r'\d+', '', all_text)
    
    # Kelimelere böl
    words = all_text.split()
    
    # Minimum uzunluk filtresi
    words = [word for word in words if len(word) >= min_word_length]
    
    # Özel karakterleri temizle
    import string
    words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words]
    words = [word for word in words if word and len(word) >= min_word_length]
    
    # Varsayılan Türkçe stopwords
    default_stopwords = {
        'bir', 'bu', 'da', 'de', 've', 'ki', 'mi', 'mu', 'mü', 'için', 'ile', 'gibi',
        'daha', 'en', 'çok', 'var', 'yok', 'olan', 'olarak', 'hem', 'ya', 'veya',
        'ama', 'ancak', 'fakat', 'lakin', 'şu', 'o', 'ben', 'sen', 'biz', 'siz',
        'onlar', 'kendi', 'her', 'hiç', 'bazı', 'tüm', 'bütün', 'kadar', 'sonra',
        'önce', 'şimdi', 'bugün', 'dün', 'yarın', 'ne', 'nasıl', 'neden', 'niçin',
        'nerede', 'ne', 'hangi', 'kim', 'kimin', 'kime', 'kimden', 'artık', 'hala',
        'henüz', 'sadece', 'yalnız', 'bile', 'dahi', 'rağmen', 'karşın', 'https', 'www', 'com', 'tr', 'org', 'net', 'edu', 'gov', 'mil', 'biz', 'sen', 'biz', 'siz',
        'onlar', 'kendi', 'her', 'hiç', 'bazı', 'tüm', 'bütün', 'kadar', 'sonra',
        'önce', 'şimdi', 'bugün', 'dün', 'yarın', 'ne', 'nasıl', 'neden', 'niçin',
        'nerede', 'ne', 'hangi', 'kim', 'kimin', 'kime', 'kimden', 'artık', 'hala',
        'henüz', 'sadece', 'yalnız', 'bile', 'dahi', 'rağmen', 'karşın', 'https', 'www', 'com', 'tr', 'org', 'net', 'edu', 'gov', 'mil', 'biz', 'sen', 'biz', 'siz',
        'onlar', 'kendi', 'her', 'hiç', 'bazı', 'tüm', 'bütün', 'kadar', 'sonra',
        'önce', 'şimdi', 'bugün', 'dün', 'yarın', 'ne', 'nasıl', 'neden', 'niçin'    
    }
    
    # Özel stopwords ekle
    if custom_stopwords:
        default_stopwords.update(set(custom_stopwords))
    
    # Stopwords'leri kaldır
    words = [word for word in words if word not in default_stopwords]
    
    # Kelime frekanslarını hesapla
    word_freq = Counter(words)
    
    # İşlenmiş metni geri oluştur
    processed_text = ' '.join(words)
    
    print(f"📊 Toplam benzersiz kelime: {len(word_freq)}")
    print(f"📄 İşlenmiş metin uzunluğu: {len(processed_text)} karakter")
    
    return processed_text, word_freq

def _load_shape_mask(shape_mask_path):
    """Özel şekil maskesi yükle"""
    try:
        mask_image = Image.open(shape_mask_path).convert('RGB')
        mask_array = np.array(mask_image)
        print(f"🎭 Şekil maskesi yüklendi: {shape_mask_path}")
        return mask_array
    except Exception as e:
        print(f"⚠️ Şekil maskesi yüklenemedi: {e}")
        return None

def _create_main_wordcloud(processed_text, cikti_klasoru, max_words, color_scheme, mask_array):
    """Ana kelime bulutunu oluştur"""
    print("🎨 Ana kelime bulutu oluşturuluyor...")
    
    # WordCloud parametreleri
    wc_params = {
        'width': 1200 if mask_array is None else mask_array.shape[1],
        'height': 800 if mask_array is None else mask_array.shape[0],
        'background_color': 'white',
        'max_words': max_words,
        'contour_width': 2,
        'contour_color': 'navy',
        'collocations': False,
        'colormap': color_scheme,
        'relative_scaling': 0.6,
        'min_font_size': 12,
        'max_font_size': 100,
        'prefer_horizontal': 0.7,
        'min_word_length': 2,
        'stopwords': set()  # Zaten temizledik
    }
    
    if mask_array is not None:
        wc_params['mask'] = mask_array
        wc_params['contour_color'] = 'steelblue'
    
    # Kelime bulutunu oluştur
    wordcloud = WordCloud(**wc_params).generate(processed_text)
    
    # Görselleştir
    plt.figure(figsize=(16, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Kelime Bulutu', fontsize=20, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Kaydet
    plt.savefig(os.path.join(cikti_klasoru, 'ana_kelime_bulutu.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✅ Ana kelime bulutu kaydedildi.")

def _create_multiple_wordclouds(processed_text, word_freq, cikti_klasoru, max_words):
    """Farklı renk şemaları ile çoklu kelime bulutları oluştur"""
    print("🌈 Çoklu renk şemaları ile kelime bulutları oluşturuluyor...")
    
    # Farklı renk şemaları
    color_schemes = [
        ('Viridis', 'viridis'),
        ('Plasma', 'plasma'),
        ('Inferno', 'inferno'),
        ('Cool', 'cool'),
        ('Spring', 'spring'),
        ('Ocean', 'ocean')
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Farklı Renk Şemaları ile Kelime Bulutları', fontsize=16, fontweight='bold')
    
    for idx, (name, colormap) in enumerate(color_schemes):
        row = idx // 3
        col = idx % 3
        
        try:
            # Kelime bulutu oluştur
            wordcloud = WordCloud(
                width=400, height=300,
                background_color='white',
                max_words=max_words//2,
                colormap=colormap,
                relative_scaling=0.5,
                min_font_size=8
            ).generate(processed_text)
            
            # Subplot'a yerleştir
            axes[row, col].imshow(wordcloud, interpolation='bilinear')
            axes[row, col].set_title(f'{name} Teması', fontweight='bold')
            axes[row, col].axis('off')
            
        except Exception as e:
            print(f"⚠️ {name} teması oluşturulamadı: {e}")
            axes[row, col].text(0.5, 0.5, f'{name}\nHata!', 
                               ha='center', va='center', transform=axes[row, col].transAxes)
            axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_klasoru, 'coklu_kelime_bulutlari.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def _create_word_statistics(word_freq, df_clean, metin_kolonu, cikti_klasoru):
    """Kelime istatistikleri ve grafikler oluştur"""
    print("📊 Kelime istatistikleri oluşturuluyor...")
    
    # En sık kullanılan kelimeleri al
    top_words = word_freq.most_common(20)
    
    if not top_words:
        print("⚠️ İstatistik oluşturmak için yeterli kelime bulunamadı.")
        return
    
    # 1. Bar grafiği
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # En sık kullanılan kelimeler - Bar Chart
    words, counts = zip(*top_words)
    colors = plt.cm.viridis(np.linspace(0, 1, len(words)))
    
    bars = ax1.bar(range(len(words)), counts, color=colors, alpha=0.8)
    ax1.set_xlabel('Kelimeler', fontweight='bold')
    ax1.set_ylabel('Frekans', fontweight='bold')
    ax1.set_title('En Sık Kullanılan 20 Kelime', fontweight='bold', fontsize=14)
    ax1.set_xticks(range(len(words)))
    ax1.set_xticklabels(words, rotation=45, ha='right')
    
    # Bar'ların üzerine değer ekle
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 2. Horizontal Bar Chart
    ax2.barh(range(len(words)), counts, color=colors, alpha=0.8)
    ax2.set_xlabel('Frekans', fontweight='bold')
    ax2.set_ylabel('Kelimeler', fontweight='bold')
    ax2.set_title('Kelime Frekansları (Yatay)', fontweight='bold', fontsize=14)
    ax2.set_yticks(range(len(words)))
    ax2.set_yticklabels(words)
    
    # 3. Pie Chart - Top 10
    top_10_words = word_freq.most_common(10)
    if len(top_10_words) >= 5:  # En az 5 kelime varsa pie chart yap
        words_pie, counts_pie = zip(*top_10_words)
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(words_pie)))
        
        wedges, texts, autotexts = ax3.pie(counts_pie, labels=words_pie, autopct='%1.1f%%',
                                          colors=colors_pie, startangle=90)
        ax3.set_title('En Sık Kullanılan 10 Kelime (%)', fontweight='bold', fontsize=14)
        
        # Pie chart etiketlerini güzelleştir
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
    else:
        ax3.text(0.5, 0.5, 'Pie chart için\nyeterli veri yok', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
        ax3.axis('off')
    
    # 4. Kelime uzunluğu dağılımı
    word_lengths = [len(word) for word in word_freq.keys()]
    ax4.hist(word_lengths, bins=range(min(word_lengths), max(word_lengths) + 2), 
             alpha=0.7, color='skyblue', edgecolor='black')
    ax4.set_xlabel('Kelime Uzunluğu', fontweight='bold')
    ax4.set_ylabel('Frekans', fontweight='bold')
    ax4.set_title('Kelime Uzunluğu Dağılımı', fontweight='bold', fontsize=14)
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_klasoru, 'kelime_istatistikleri.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # İstatistikleri dosyaya kaydet
    _save_word_statistics(word_freq, df_clean, metin_kolonu, cikti_klasoru)

def _save_word_statistics(word_freq, df_clean, metin_kolonu, cikti_klasoru):
    """Kelime istatistiklerini dosyaya kaydet"""
    
    # Detaylı istatistikleri kaydet
    with open(os.path.join(cikti_klasoru, 'kelime_istatistikleri.txt'), 'w', encoding='utf-8') as f:
        f.write("KELIME İSTATİSTİKLERİ\n")
        f.write("="*50 + "\n\n")
        
        f.write(f"Toplam metin sayısı: {len(df_clean)}\n")
        f.write(f"Toplam benzersiz kelime: {len(word_freq)}\n")
        f.write(f"Toplam kelime kullanımı: {sum(word_freq.values())}\n")
        f.write(f"Ortalama kelime uzunluğu: {np.mean([len(word) for word in word_freq.keys()]):.1f}\n\n")
        
        f.write("EN SIK KULLANILAN 50 KELİME:\n")
        f.write("-"*30 + "\n")
        for idx, (word, count) in enumerate(word_freq.most_common(50), 1):
            f.write(f"{idx:2d}. {word:15s}: {count:4d} kez\n")
    
    # CSV formatında da kaydet
    top_words_df = pd.DataFrame(word_freq.most_common(100), 
                               columns=['Kelime', 'Frekans'])
    top_words_df['Sira'] = range(1, len(top_words_df) + 1)
    top_words_df = top_words_df[['Sira', 'Kelime', 'Frekans']]
    
    top_words_df.to_csv(os.path.join(cikti_klasoru, 'en_sik_kelimeler.csv'), 
                        index=False, encoding='utf-8')

def _print_wordcloud_summary(word_freq, total_texts):
    """Özet bilgileri yazdır"""
    print("\n" + "="*50)
    print("📊 KELİME BULUTU ANALİZİ ÖZETİ")
    print("="*50)
    print(f"📄 Toplam metin sayısı: {total_texts}")
    print(f"🔤 Benzersiz kelime sayısı: {len(word_freq)}")
    print(f"📝 Toplam kelime kullanımı: {sum(word_freq.values())}")
    print(f"📏 Ortalama kelime uzunluğu: {np.mean([len(word) for word in word_freq.keys()]):.1f}")
    
    print(f"\n🏆 EN SIK KULLANILAN 10 KELİME:")
    print("-"*30)
    for idx, (word, count) in enumerate(word_freq.most_common(10), 1):
        print(f"{idx:2d}. {word:12s}: {count:4d} kez")
    print("="*50)

