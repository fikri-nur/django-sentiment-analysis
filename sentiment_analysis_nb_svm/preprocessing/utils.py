import os
import re
from ast import literal_eval
import json
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def clean_text(text):
    # Mengganti kata berulang seperti "pagi-pagi" menjadi "pagi"
    text = re.sub(r'\b(\w+)(?:-\1)+\b', r'\1', text)
    text = re.sub(r'\b(\w+)-\1\b', r'\1', text, flags=re.IGNORECASE)

    # Memperbarui ekspresi reguler untuk hanya menghapus tautan URL
    text = re.sub(r'(?:https?|ftp):\/\/[\S]+|www\.[\S]+', '', text, flags=re.MULTILINE)

    # Menghilangkan karakter yang tidak diinginkan selain emoji
    text = re.sub(r'[^A-Za-z\s]', '', text)

    # Menghilangkan spasi berlebih
    text = re.sub(r'\s+', ' ', text)

    # Menghapus spasi tambahan di awal dan akhir teks
    text = text.strip()

    return text

def case_folding(text):
    return text.lower()
    
def tokenize_text(text):
    return re.findall(r'\b\w+\b', text)

def read_slang_words(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    with open(file_path, 'r') as file:
        slang_words = json.load(file)
    return slang_words

def normalize_text_with_slang(text, slang_words):
    # Jika input adalah string yang direpresentasikan sebagai list, ubah menjadi list
    if isinstance(text, str) and text.startswith('[') and text.endswith(']'):
        text = literal_eval(text)
    
    # Jika input adalah list, gabungkan menjadi string
    if isinstance(text, list):
        text = ' '.join(text)
    
    normalized_text = text
    for slang, replacement in slang_words.items():
        # Mencari kata slang yang berdiri sendiri dalam teks menggunakan regex
        regex = r"\b" + re.escape(slang) + r"\b"
        # Melakukan penggantian hanya pada kata-kata yang berdiri sendiri
        normalized_text = re.sub(regex, replacement, normalized_text)
    
    # Mengembalikan teks yang dinormalisasi dalam bentuk token (list kata)
    return normalized_text.split()

def read_stopwords(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    stopwords = set()
    with open(file_path, 'r') as file:
        for line in file:
            stopwords.add(line.strip())
    return stopwords

def remove_stopwords(text, stopwords):
    # Jika input adalah string yang direpresentasikan sebagai list, ubah menjadi list
    if isinstance(text, str) and text.startswith('[') and text.endswith(']'):
        text = literal_eval(text)
    
    # Jika input adalah list, gabungkan menjadi string
    if isinstance(text, list):
        text = ' '.join(text)
    
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return filtered_words  # Kembalikan sebagai list (token)

def read_stemming_words(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    stemming_words = set()
    with open(file_path, 'r') as file:
        for line in file:
            stemming_words.add(line.strip())
    return stemming_words

def apply_stemming(text, stemming_words):
    # Initialize Sastrawi stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    
    if isinstance(text, str) and text.startswith('[') and text.endswith(']'):
        text = literal_eval(text)

    if isinstance(text, list):
        text = ' '.join(text)
    
    # Apply stemming using Sastrawi
    stemmed_text = stemmer.stem(text)
    
    return stemmed_text.split()

def apply_sastrawi_stemming(text):
    # Initialize Sastrawi stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    
    # Apply stemming using Sastrawi
    return stemmer.stem(text)