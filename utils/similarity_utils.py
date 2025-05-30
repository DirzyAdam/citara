import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, text_splitter_func):
    """
    Fungsi generik untuk mencari kemiripan antara citation_text dan setiap unit (kalimat/paragraf) pada pages_text.
    """
    matches = []
    total_pages = len(pages_text)
    semantic_model = None
    if method == "semantic":
        from utils.semantic_utils import get_semantic_model, compute_semantic_similarity_batch
        semantic_model = get_semantic_model()
    vectorizer = None
    if method == "tfidf":
        vectorizer = TfidfVectorizer()
    for idx, (page, text) in enumerate(pages_text.items()):
        if not text:
            if progress_callback:
                progress_callback(idx + 1, total_pages)
            continue
        text_units = text_splitter_func(text)
        if not text_units:
            if progress_callback:
                progress_callback(idx + 1, total_pages)
            continue
        if method == "semantic":
            if semantic_model is None:
                from utils.semantic_utils import get_semantic_model, compute_semantic_similarity_batch
                semantic_model = get_semantic_model()
            scores = compute_semantic_similarity_batch(citation_text, text_units, semantic_model)
            for unit, cos_sim in zip(text_units, scores):
                if cos_sim >= similarity_threshold:
                    matches.append((page, unit, float(cos_sim)))
        else:
            if vectorizer is None:
                vectorizer = TfidfVectorizer()
            for unit in text_units:
                corpus = [citation_text, unit]
                vectors = vectorizer.fit_transform(corpus)
                cos_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                if cos_sim >= similarity_threshold:
                    matches.append((page, unit, cos_sim))
        if progress_callback:
            progress_callback(idx + 1, total_pages)
    return matches

def find_sentence_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None):
    """
    Membagi teks per halaman menjadi kalimat dan menghitung cosine similarity
    antara teks sitasi (hasil terjemahan) dengan tiap kalimat PDF.
    """
    def sentence_splitter(text_content):
        return nltk.tokenize.sent_tokenize(text_content)
    return _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, sentence_splitter)

def find_paragraph_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None):
    """
    Membagi teks per halaman menjadi paragraf (asumsi paragraf dipisahkan oleh "\\n\\n")
    dan menghitung cosine similarity antara teks sitasi (hasil terjemahan)
    dengan tiap paragraf PDF.
    """
    def paragraph_splitter(text_content):
        return [p.strip() for p in text_content.split("\n\n") if p.strip()]
    return _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, paragraph_splitter)
