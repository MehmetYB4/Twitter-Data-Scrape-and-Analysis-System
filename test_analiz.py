#!/usr/bin/env python3
"""
Hızlı test analizi - 20 tweet için süre ölçümü
"""

import pandas as pd
import json
import time
from datetime import datetime

print("🚀 Hızlı Test Analizi Başlatılıyor...")

# Test verilerini yükle
with open('tweet_arsivleri/test_tweets.json', 'r', encoding='utf-8') as f:
    tweets = json.load(f)

df = pd.DataFrame({'temiz_metin': tweets})
print(f"📄 {len(tweets)} tweet yüklendi")

# 1. Kelime Bulutu Testi (En Hızlı)
print("\n1️⃣ Kelime Bulutu Testi...")
start_time = time.time()
try:
    from analiz.wordcloud.wordcloud_olustur import wordcloud_olustur
    result = wordcloud_olustur(df, cikti_klasoru='test_output')
    end_time = time.time()
    print(f"✅ Kelime Bulutu: {end_time - start_time:.2f} saniye - {'Başarılı' if result else 'Başarısız'}")
except Exception as e:
    print(f"❌ Kelime Bulutu Hatası: {e}")

# 2. LDA Testi (Orta)
print("\n2️⃣ LDA Testi...")
start_time = time.time()
try:
    from analiz.lda.lda_analizi import lda_analizi
    result = lda_analizi(df, cikti_klasoru='test_output', num_topics=2, iterations=10)
    end_time = time.time()
    print(f"✅ LDA: {end_time - start_time:.2f} saniye - {'Başarılı' if result else 'Başarısız'}")
except Exception as e:
    print(f"❌ LDA Hatası: {e}")

# 3. Duygu Analizi Testi (En Yavaş - Model İndirme)
print("\n3️⃣ Duygu Analizi Testi...")
start_time = time.time()
try:
    from analiz.sentiment.duygu_analizi import duygu_analizi
    print("📥 BERT model indiriliyor (ilk kez uzun sürebilir)...")
    result = duygu_analizi(df, cikti_klasoru='test_output', batch_size=8)
    end_time = time.time()
    print(f"✅ Duygu Analizi: {end_time - start_time:.2f} saniye - {'Başarılı' if result else 'Başarısız'}")
except Exception as e:
    print(f"❌ Duygu Analizi Hatası: {e}")

print("\n�� Test Tamamlandı!") 