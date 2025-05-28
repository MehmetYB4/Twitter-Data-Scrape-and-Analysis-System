# -*- coding: utf-8 -*-
"""
Gelişmiş Ön İşleme Modülü
Kapsamlı text temizleme, normalizasyon ve ön işleme fonksiyonları
"""

import re
import string
import unicodedata
from typing import List, Union


# Genişletilmiş Türkçe stopwords listesi
TURKISH_STOPWORDS = {
    've', 'bir', 'bu', 'da', 'de', 'için', 'ile', 'o', 'ki', 'çok', 'var', 'olan', 'olarak', 'ne',
    'daha', 'kadar', 'en', 'ama', 'ya', 'sadece', 'son', 'şu', 've', 'tüm', 'kendi', 'gibi', 'bana',
    'sana', 'ona', 'bize', 'size', 'onlara', 'benim', 'senin', 'onun', 'bizim', 'sizin', 'onların',
    'ben', 'sen', 'biz', 'siz', 'onlar', 'şey', 'şeyi', 'şeyle', 'şeyin', 'şeyden', 'şeyde', 'şeye',
    'neden', 'nasıl', 'nerede', 'ne', 'kim', 'hangi', 'kaç', 'hem', 'hiç', 'her', 'hep', 'hele',
    'hala', 'hâlâ', 'henüz', 'hemen', 'hele', 'hadi', 'haydi', 'işte', 'artık', 'zaten', 'yine',
    'gene', 'tekrar', 'yeniden', 'başka', 'diğer', 'öbür', 'öteki', 'beriki', 'şöyle', 'böyle',
    'öyle', 'aynı', 'benzer', 'farklı', 'başka', 'birçok', 'pek', 'oldukça', 'fazla', 'az', 'biraz',
    'az', 'çok', 'tam', 'yarım', 'buçuk', 'epey', 'hayli', 'iyice', 'oldukça', 'bir', 'iki', 'üç',
    'şimdi', 'bugün', 'yarın', 'dün', 'önceki', 'sonraki', 'gelecek', 'geçen', 'bu', 'şu', 'o',
    'buraya', 'şuraya', 'oraya', 'burada', 'şurada', 'orada', 'buradan', 'şuradan', 'oradan',
    'yukarı', 'aşağı', 'ileri', 'geri', 'sağ', 'sol', 'ön', 'arka', 'iç', 'dış', 'alt', 'üst',
    'oldu', 'olur', 'oluyor', 'olacak', 'olmuş', 'olmak', 'var', 'yok', 'vardı', 'yoktu', 'oldu',
    'değil', 'değildi', 'değilmiş', 'mı', 'mi', 'mu', 'mü', 'ise', 'imiş', 'ken', 'iken', 'diye',
    'kez', 'defa', 'sefer', 'gün', 'hafta', 'ay', 'yıl', 'asır', 'çağ', 'dönem', 'zaman', 'vakit',
    'fakat', 'ancak', 'lakin', 'yoksa', 'eğer', 'madem', 'çünkü', 'için', 'dolayı', 'sayesinde',
    'rağmen', 'karşın', 'göre', 'dair', 'kadar', 'değin', 'beri', 'önce', 'sonra', 'sırada',
    'arasında', 'içinde', 'dışında', 'üzerinde', 'altında', 'yanında', 'karşısında', 'arkasında',
    'ile', 'den', 'dan', 'ten', 'tan', 'nin', 'nın', 'nün', 'nun', 'ye', 'ya', 'e', 'a',
    'i', 'ı', 'u', 'ü', 'o', 'ö', 'de', 'da', 'te', 'ta', 'ne', 'na', 'le', 'la',
    'ler', 'lar', 'dir', 'dır', 'dur', 'dür', 'tir', 'tır', 'tur', 'tür'
}

# URL ve özel karakter regex patterns
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
MENTION_PATTERN = re.compile(r'@\w+')
HASHTAG_PATTERN = re.compile(r'#\w+')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(\+90|0)?[0-9]{3}[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}')
NUMBER_PATTERN = re.compile(r'\b\d+\b')
EMOJI_PATTERN = re.compile(r'[^\w\s\u00C0-\u024F\u1E00-\u1EFF]')
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')


def remove_urls(text: str) -> str:
    """URL'leri kaldırır"""
    return URL_PATTERN.sub('', text)


def remove_html_tags(text: str) -> str:
    """HTML etiketlerini kaldırır"""
    return HTML_TAG_PATTERN.sub('', text)


def remove_mentions(text: str) -> str:
    """@mentions kaldırır"""
    return MENTION_PATTERN.sub('', text)


def remove_hashtags(text: str, keep_text: bool = False) -> str:
    """Hashtag'leri kaldırır veya sadece # işaretini kaldırır"""
    if keep_text:
        return text.replace('#', '')
    return HASHTAG_PATTERN.sub('', text)


def remove_emails(text: str) -> str:
    """E-mail adreslerini kaldırır"""
    return EMAIL_PATTERN.sub('', text)


def remove_phone_numbers(text: str) -> str:
    """Telefon numaralarını kaldırır"""
    return PHONE_PATTERN.sub('', text)


def remove_numbers(text: str) -> str:
    """Sayıları kaldırır"""
    return NUMBER_PATTERN.sub('', text)


def remove_emojis(text: str) -> str:
    """Emoji ve özel karakterleri kaldırır"""
    return EMOJI_PATTERN.sub('', text)


def remove_punctuation(text: str) -> str:
    """Noktalama işaretlerini kaldırır"""
    return PUNCTUATION_PATTERN.sub(' ', text)


def normalize_turkish_chars(text: str) -> str:
    """Türkçe karakterleri normalize eder"""
    replacements = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    return text


def normalize_unicode(text: str) -> str:
    """Unicode karakterleri normalize eder"""
    return unicodedata.normalize('NFKD', text)


def remove_extra_whitespace(text: str) -> str:
    """Fazla boşlukları kaldırır"""
    return re.sub(r'\s+', ' ', text).strip()


def remove_repeated_chars(text: str, max_repeat: int = 2) -> str:
    """Tekrarlanan karakterleri sınırlar (örn: 'çookkkk' -> 'çook')"""
    pattern = r'(.)\1{' + str(max_repeat) + ',}'
    return re.sub(pattern, r'\1' * max_repeat, text)


def filter_by_length(words: List[str], min_length: int = 2, max_length: int = 50) -> List[str]:
    """Kelime uzunluğuna göre filtreler"""
    return [word for word in words if min_length <= len(word) <= max_length]


def remove_stopwords(words: List[str], custom_stopwords: set = None) -> List[str]:
    """Stopword'leri kaldırır"""
    stopwords = TURKISH_STOPWORDS.copy()
    if custom_stopwords:
        stopwords.update(custom_stopwords)
    return [word for word in words if word.lower() not in stopwords]


def filter_by_frequency(words: List[str], min_freq: int = 1, max_freq: int = None) -> List[str]:
    """Frekansa göre filtreler"""
    from collections import Counter
    word_counts = Counter(words)
    
    if max_freq is None:
        max_freq = len(words)
    
    return [word for word in words 
            if min_freq <= word_counts[word] <= max_freq]


def basic_preprocess(text: str, 
                    lowercase: bool = True,
                    remove_urls_flag: bool = True,
                    remove_html_flag: bool = True,
                    remove_mentions_flag: bool = True,
                    remove_hashtags_flag: bool = True,
                    remove_emails_flag: bool = True,
                    remove_phones_flag: bool = True,
                    remove_numbers_flag: bool = True,
                    remove_emojis_flag: bool = True,
                    remove_punctuation_flag: bool = True,
                    normalize_chars: bool = False,
                    remove_extra_spaces: bool = True) -> str:
    """
    Temel text ön işleme fonksiyonu
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    # URL'leri kaldır
    if remove_urls_flag:
        text = remove_urls(text)
    
    # HTML etiketlerini kaldır
    if remove_html_flag:
        text = remove_html_tags(text)
    
    # Mention'ları kaldır
    if remove_mentions_flag:
        text = remove_mentions(text)
    
    # Hashtag'leri kaldır
    if remove_hashtags_flag:
        text = remove_hashtags(text)
    
    # E-mail'leri kaldır
    if remove_emails_flag:
        text = remove_emails(text)
    
    # Telefon numaralarını kaldır
    if remove_phones_flag:
        text = remove_phone_numbers(text)
    
    # Sayıları kaldır
    if remove_numbers_flag:
        text = remove_numbers(text)
    
    # Emoji'leri kaldır
    if remove_emojis_flag:
        text = remove_emojis(text)
    
    # Noktalama işaretlerini kaldır
    if remove_punctuation_flag:
        text = remove_punctuation(text)
    
    # Türkçe karakterleri normalize et
    if normalize_chars:
        text = normalize_turkish_chars(text)
    
    # Unicode normalize
    text = normalize_unicode(text)
    
    # Fazla boşlukları kaldır
    if remove_extra_spaces:
        text = remove_extra_whitespace(text)
    
    return text


def advanced_preprocess(text: str,
                       min_word_length: int = 2,
                       max_word_length: int = 50,
                       remove_stopwords_flag: bool = True,
                       custom_stopwords: set = None,
                       min_frequency: int = 1,
                       max_frequency: int = None,
                       max_char_repeat: int = 2) -> List[str]:
    """
    Gelişmiş text ön işleme fonksiyonu
    Text'i önce temel ön işlemeden geçirir, sonra kelime bazlı işlemler yapar
    """
    # Önce temel ön işleme
    processed_text = basic_preprocess(text)
    
    # Tekrarlanan karakterleri sınırla
    if max_char_repeat > 0:
        processed_text = remove_repeated_chars(processed_text, max_char_repeat)
    
    # Kelimelere ayır
    words = processed_text.split()
    
    # Uzunluğa göre filtrele
    words = filter_by_length(words, min_word_length, max_word_length)
    
    # Stopword'leri kaldır
    if remove_stopwords_flag:
        words = remove_stopwords(words, custom_stopwords)
    
    # Frekansa göre filtrele
    if min_frequency > 1 or max_frequency is not None:
        words = filter_by_frequency(words, min_frequency, max_frequency)
    
    return words


def preprocess_for_lda(text: str) -> List[str]:
    """LDA analizi için özel ön işleme"""
    return advanced_preprocess(
        text,
        min_word_length=3,
        max_word_length=30,
        remove_stopwords_flag=True,
        min_frequency=2,
        max_char_repeat=2
    )


def preprocess_for_sentiment(text: str) -> str:
    """Sentiment analizi için özel ön işleme"""
    return basic_preprocess(
        text,
        remove_urls_flag=True,
        remove_html_flag=True,
        remove_mentions_flag=True,
        remove_hashtags_flag=False,  # Hashtag'ler sentiment için önemli olabilir
        remove_emails_flag=True,
        remove_phones_flag=True,
        remove_numbers_flag=False,   # Sayılar sentiment için önemli olabilir
        remove_emojis_flag=False,    # Emoji'ler sentiment için önemli
        remove_punctuation_flag=False,  # Noktalama sentiment için önemli
        normalize_chars=False
    )


def preprocess_for_wordcloud(text: str) -> List[str]:
    """Word cloud için özel ön işleme"""
    return advanced_preprocess(
        text,
        min_word_length=3,
        max_word_length=25,
        remove_stopwords_flag=True,
        min_frequency=2,
        max_char_repeat=2
    )


def batch_preprocess(texts: List[str], 
                    preprocess_func,
                    show_progress: bool = False) -> List[Union[str, List[str]]]:
    """
    Toplu text ön işleme fonksiyonu
    """
    results = []
    total = len(texts)
    
    for i, text in enumerate(texts):
        if show_progress and i % 100 == 0:
            print(f"İşlenen: {i}/{total} ({i/total*100:.1f}%)")
        
        processed = preprocess_func(text)
        results.append(processed)
    
    if show_progress:
        print(f"Tamamlandı: {total}/{total} (100.0%)")
    
    return results


# Backward compatibility için eski fonksiyon isimleri
def clean_text(text: str) -> str:
    """Geriye uyumluluk için - basic_preprocess ile aynı"""
    return basic_preprocess(text)


def tokenize_and_clean(text: str) -> List[str]:
    """Geriye uyumluluk için - advanced_preprocess ile aynı"""
    return advanced_preprocess(text)


if __name__ == "__main__":
    # Test örneği
    sample_text = """
    Merhaba! Bu bir test metnidir... 📱 http://example.com #test @kullanici
    Bu metinde çoook fazla tekrarlanan harfler var!!! 
    Email: test@example.com Tel: 0555 123 45 67
    Türkçe karakterler: çğıöşü 123456
    """
    
    print("Orijinal text:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    
    print("Temel ön işleme:")
    print(basic_preprocess(sample_text))
    print("\n" + "="*50 + "\n")
    
    print("Gelişmiş ön işleme:")
    print(advanced_preprocess(sample_text))
    print("\n" + "="*50 + "\n")
    
    print("LDA için ön işleme:")
    print(preprocess_for_lda(sample_text))
    print("\n" + "="*50 + "\n")
    
    print("Sentiment için ön işleme:")
    print(preprocess_for_sentiment(sample_text))
    print("\n" + "="*50 + "\n")
    
    print("WordCloud için ön işleme:")
    print(preprocess_for_wordcloud(sample_text)) 