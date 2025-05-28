import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # GUI olmayan ortamlar için
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import torch
from tqdm import tqdm
import numpy as np

# Matplotlib için Türkçe font ayarları
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

def duygu_analizi(df, metin_kolonu='temiz_metin', cikti_klasoru='.', 
                  model_name='savasy/bert-base-turkish-sentiment-cased', 
                  batch_size=16, neutral_threshold=0.6):
    """
    Türkçe tweet'ler için gelişmiş duygu analizi yapar.
    
    Args:
        df: Analiz edilecek veri (DataFrame)
        metin_kolonu: Metin kolonu adı
        cikti_klasoru: Sonuçların kaydedileceği klasör
        model_name: Kullanılacak model adı
        batch_size: Batch boyutu
        neutral_threshold: Nötr sınıflandırma için eşik değeri (0.6 = %60 güven)
    """
    print(f"🎭 Duygu analizi başlatılıyor: {model_name}")
    print(f"⚙️ Batch boyutu: {batch_size}, Nötr eşiği: {neutral_threshold}")
    
    try:
        # Çıktı klasörünü oluştur
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        print("📥 Model yükleniyor...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️ Cihaz: {device}")
        
        model.to(device)
        
        # Pipeline'ı tüm skorları döndürecek şekilde ayarla
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1,
            return_all_scores=True  # Tüm skorları al
        )
        
        # Boş ve NaN metinleri temizle
        df_clean = df.dropna(subset=[metin_kolonu]).copy()
        df_clean = df_clean[df_clean[metin_kolonu].str.strip() != '']
        
        metinler = df_clean[metin_kolonu].tolist()
        print(f"📄 Toplam {len(metinler)} metin analiz edilecek...")
        
        sonuclar = []
        detayli_sonuclar = []
        
        for i in tqdm(range(0, len(metinler), batch_size), desc="🎭 Duygu Analizi"):
            batch = metinler[i:i+batch_size]
            try:
                batch_results = sentiment_analyzer(batch)
                
                for result in batch_results:
                    # Tüm skorları al
                    scores_dict = {item['label']: item['score'] for item in result}
                    
                    # En yüksek skoru bul
                    max_label = max(scores_dict, key=scores_dict.get)
                    max_score = scores_dict[max_label]
                    
                    # Nötr değerlendirmesi: eğer en yüksek skor threshold'dan düşükse NEUTRAL yap
                    if max_score < neutral_threshold:
                        final_label = 'NEUTRAL'
                        final_score = max_score
                    else:
                        final_label = max_label
                        final_score = max_score
                    
                    sonuclar.append({
                        'label': final_label,
                        'score': final_score
                    })
                    
                    # Detaylı sonuçları kaydet
                    detail = scores_dict.copy()
                    detail['final_label'] = final_label
                    detail['final_score'] = final_score
                    detayli_sonuclar.append(detail)
                    
            except Exception as e:
                print(f"⚠️ Batch {i} hatası: {e}")
                # Hata durumunda neutral etiket ekle
                for _ in batch:
                    sonuclar.append({'label': 'NEUTRAL', 'score': 0.5})
                    detayli_sonuclar.append({
                        'POSITIVE': 0.33, 'NEGATIVE': 0.33, 'NEUTRAL': 0.34,
                        'final_label': 'NEUTRAL', 'final_score': 0.5
                    })
        
        # Sonuçları DataFrame'e ekle
        df_clean['duygu_sinifi'] = [sonuc['label'] for sonuc in sonuclar]
        df_clean['duygu_skoru'] = [sonuc['score'] for sonuc in sonuclar]
        
        # Detaylı skorları ekle
        for key in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
            if key in detayli_sonuclar[0]:
                df_clean[f'{key.lower()}_skor'] = [d.get(key, 0) for d in detayli_sonuclar]
        
        # Sonuçları görselleştir - Profesyonel grafik
        _create_professional_charts(df_clean, cikti_klasoru)
        
        # Sonuçları kaydet
        save_columns = [metin_kolonu, 'duygu_sinifi', 'duygu_skoru']
        # Mevcut sütunları kontrol et ve ekle
        for col in ['positive_skor', 'negative_skor', 'neutral_skor']:
            if col in df_clean.columns:
                save_columns.append(col)
        
        df_clean[save_columns].to_csv(
            os.path.join(cikti_klasoru, 'duygu_analizi_sonuclari.csv'),
            index=False,
            encoding='utf-8'
        )
        
        # Özet istatistikleri yazdır
        _print_summary_stats(df_clean)
        
        print("✅ Duygu analizi tamamlandı.")
        
        # Analiz sonuçlarını return et
        average_scores = {}
        for score_col in ['positive_skor', 'negative_skor', 'neutral_skor']:
            if score_col in df_clean.columns:
                average_scores[score_col.replace('_skor', '')] = df_clean[score_col].mean()
        
        return {
            'dataframe': df_clean,
            'summary': {
                'total_tweets': len(df_clean),
                'sentiment_distribution': df_clean['duygu_sinifi'].value_counts().to_dict(),
                'average_scores': average_scores
            },
            'output_folder': cikti_klasoru
        }
        
    except Exception as e:
        print(f"❌ Duygu analizi sırasında bir hata oluştu: {e}")
        return None

def _create_professional_charts(df, cikti_klasoru):
    """Profesyonel görünümlü grafikler oluşturur"""
    
    # Seaborn stil ayarları
    sns.set_style("whitegrid")
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Renk paleti - Profesyonel ve göze hoş
    colors = {
        'POSITIVE': '#2E8B57',    # Sea Green
        'NEGATIVE': '#DC143C',    # Crimson  
        'NEUTRAL': '#4682B4'      # Steel Blue
    }
    
    duygu_sayilari = df['duygu_sinifi'].value_counts()
    print(f"📊 Duygu dağılımı: {dict(duygu_sayilari)}")
    
    # 1. Bar Chart - Daha profesyonel
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar chart
    bar_colors = [colors.get(label, '#708090') for label in duygu_sayilari.index]
    bars = ax1.bar(duygu_sayilari.index, duygu_sayilari.values, 
                   color=bar_colors, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Bar chart'a değer etiketleri ekle
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(duygu_sayilari.values)*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax1.set_title('Tweet Duygu Dağılımı', fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Tweet Sayısı', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Duygu Sınıfı', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Pie Chart - Yüzdeler ile
    explode_values = tuple([0.05] * len(duygu_sayilari))  # Duygu sayısına göre dinamik explode
    wedges, texts, autotexts = ax2.pie(duygu_sayilari.values, 
                                       labels=duygu_sayilari.index,
                                       colors=[colors.get(label, '#708090') for label in duygu_sayilari.index],
                                       autopct='%1.1f%%',
                                       startangle=90,
                                       explode=explode_values)
    
    # Pie chart'ı güzelleştir
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    ax2.set_title('Duygu Dağılımı Yüzdeleri', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_klasoru, 'duygu_dagilimi.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 3. Skor dağılım histogramı
    plt.figure(figsize=(12, 8))
    
    for i, (duygu, color) in enumerate(colors.items()):
        if duygu.lower() + '_skor' in df.columns:
            plt.subplot(2, 2, i+1)
            df[duygu.lower() + '_skor'].hist(bins=30, color=color, alpha=0.7, edgecolor='black')
            plt.title(f'{duygu} Skor Dağılımı', fontweight='bold')
            plt.xlabel('Skor', fontweight='bold')
            plt.ylabel('Frekans', fontweight='bold')
            plt.grid(alpha=0.3)
    
    # 4. Genel güven skoru dağılımı
    plt.subplot(2, 2, 4)
    df['duygu_skoru'].hist(bins=30, color='#9370DB', alpha=0.7, edgecolor='black')
    plt.title('Genel Güven Skoru Dağılımı', fontweight='bold')
    plt.xlabel('Güven Skoru', fontweight='bold')
    plt.ylabel('Frekans', fontweight='bold')
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_klasoru, 'skor_dagilimi.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def _print_summary_stats(df):
    """Özet istatistikleri yazdırır"""
    print("\n" + "="*50)
    print("📈 DUYGU ANALİZİ ÖZETİ")
    print("="*50)
    
    total = len(df)
    duygu_sayilari = df['duygu_sinifi'].value_counts()
    
    for duygu, sayi in duygu_sayilari.items():
        yuzde = (sayi / total) * 100
        print(f"{duygu:>10}: {sayi:>6} tweet ({yuzde:>5.1f}%)")
    
    print(f"{'TOPLAM':>10}: {total:>6} tweet")
    print("="*50)
    
    # Ortalama güven skorları
    print("\n📊 ORTALAMA GÜVEN SKORLARI:")
    print("-"*30)
    for col in ['positive_skor', 'negative_skor', 'neutral_skor']:
        if col in df.columns:
            avg_score = df[col].mean()
            print(f"{col.replace('_skor', '').upper():>10}: {avg_score:.3f}")
    
    print(f"{'GENEL':>10}: {df['duygu_skoru'].mean():.3f}")

# Gelişmiş kullanım örneği:
if __name__ == "__main__":
    # Örnek veri oluştur (gerçek kullanımda CSV'den okuyun)
    sample_data = {
        'temiz_metin': [
            'Bu ürün gerçekten harika, çok memnunum!',
            'Berbat bir deneyim yaşadım, hiç beğenmedim.',
            'Normal bir ürün, ne iyi ne kötü.',
            'Müthiş kalite, herkese tavsiye ederim!',
            'Fena değil ama daha iyisi olabilir.'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Analizi çalıştır
    sonuc_df = duygu_analizi(
        df=df, 
        metin_kolonu='temiz_metin', 
        cikti_klasoru='sentiment_results',
        neutral_threshold=0.65  # %65 güven eşiği
    )
    
    if sonuc_df is not None:
        print("\n✅ Analiz tamamlandı! Sonuçlar 'sentiment_results' klasöründe.")