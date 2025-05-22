import os
import dotenv
import deepl
import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from sentence_transformers import SentenceTransformer, util

dotenv.load_dotenv()

# Pastikan resource NLTK telah diunduh
nltk.download('punkt', quiet=True)

# Ambil API key DeepL dari environment variable
DeepL_API_KEY = os.getenv("DeepL_API_KEY")
if not DeepL_API_KEY:
    raise ValueError("DeepL_API_KEY belum diset. Pastikan environment variable DeepL_API_KEY sudah diset.")

# Inisialisasi translator dari library DeepL
translator = deepl.Translator(DeepL_API_KEY)

# Inisialisasi model untuk representasi semantik (Sentence-BERT)
semantic_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")


def translate_text_from_ID_to_EN(text):
    """
    Menerjemahkan teks dari Bahasa Indonesia ke Bahasa Inggris (EN-US)
    menggunakan DeepL API melalui library DeepL.
    """
    result = translator.translate_text(text, source_lang="ID", target_lang="EN-US")
    return result.text


def extract_text_by_page(pdf_path):
    """
    Mengekstrak teks dari setiap halaman file PDF dan mengembalikannya
    sebagai dictionary dengan nomor halaman sebagai key.
    """
    pages_text = {}
    try:
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                pages_text[page_num + 1] = page_text
        return pages_text
    except Exception as e:
        print("Error membaca file PDF:", e)
        return {}


def compute_semantic_similarity(text1, text2):
    """
    Menghitung cosine similarity antara dua teks menggunakan
    model embedding Sentence-BERT.
    """
    embedding1 = semantic_model.encode(text1, convert_to_tensor=True)
    embedding2 = semantic_model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()


def find_sentence_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf"):
    """
    Membagi teks per halaman menjadi kalimat dan menghitung cosine similarity
    antara teks sitasi (hasil terjemahan) dengan tiap kalimat PDF.
    
    Parameter:
      - method: "tfidf" (default) atau "semantic". Jika "semantic", perhitungan
                dilakukan dengan representasi embedding dari Sentence-BERT.
    """
    matches = []
    for page, text in pages_text.items():
        if not text:
            continue
        # Memecah teks menjadi kalimat dengan NLTK
        sentences = nltk.tokenize.sent_tokenize(text)
        for sentence in sentences:
            if method == "semantic":
                cos_sim = compute_semantic_similarity(citation_text, sentence)
            else:
                corpus = [citation_text, sentence]
                vectorizer = TfidfVectorizer().fit(corpus)
                vectors = vectorizer.transform(corpus)
                cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
            if cos_sim >= similarity_threshold:
                matches.append((page, sentence, cos_sim))
    return matches


def find_paragraph_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf"):
    """
    Membagi teks per halaman menjadi paragraf (asumsi paragraf dipisahkan oleh "\n\n")
    dan menghitung cosine similarity antara teks sitasi (hasil terjemahan)
    dengan tiap paragraf PDF.
    
    Parameter:
      - method: "tfidf" (default) atau "semantic". Jika "semantic", perhitungan
                dilakukan dengan representasi embedding dari Sentence-BERT.
    """
    matches = []
    for page, text in pages_text.items():
        if not text:
            continue
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for paragraph in paragraphs:
            if method == "semantic":
                cos_sim = compute_semantic_similarity(citation_text, paragraph)
            else:
                corpus = [citation_text, paragraph]
                vectorizer = TfidfVectorizer().fit(corpus)
                vectors = vectorizer.transform(corpus)
                cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
            if cos_sim >= similarity_threshold:
                matches.append((page, paragraph, cos_sim))
    return matches