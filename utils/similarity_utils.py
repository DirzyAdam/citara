import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_sentence_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None):
    """
    Membagi teks per halaman menjadi kalimat dan menghitung cosine similarity
    antara teks sitasi (hasil terjemahan) dengan tiap kalimat PDF.
    """
    matches = []
    total_pages = len(pages_text)
    semantic_model = None
    if method == "semantic":
        from utils.semantic_utils import get_semantic_model, compute_semantic_similarity_batch
        semantic_model = get_semantic_model()
    for idx, (page, text) in enumerate(pages_text.items()):
        if not text:
            continue
        sentences = nltk.tokenize.sent_tokenize(text)
        if method == "semantic":
            scores = compute_semantic_similarity_batch(citation_text, sentences, semantic_model)
            for sent, cos_sim in zip(sentences, scores):
                if cos_sim >= similarity_threshold:
                    matches.append((page, sent, float(cos_sim)))
        else:
            for sentence in sentences:
                corpus = [citation_text, sentence]
                vectorizer = TfidfVectorizer().fit(corpus)
                vectors = vectorizer.transform(corpus)
                cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
                if cos_sim >= similarity_threshold:
                    matches.append((page, sentence, cos_sim))
        if progress_callback:
            progress_callback(idx + 1, total_pages)
    return matches

def find_paragraph_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None):
    """
    Membagi teks per halaman menjadi paragraf (asumsi paragraf dipisahkan oleh "\n\n")
    dan menghitung cosine similarity antara teks sitasi (hasil terjemahan)
    dengan tiap paragraf PDF.
    """
    matches = []
    total_pages = len(pages_text)
    semantic_model = None
    if method == "semantic":
        from utils.semantic_utils import get_semantic_model, compute_semantic_similarity_batch
        semantic_model = get_semantic_model()
    for idx, (page, text) in enumerate(pages_text.items()):
        if not text:
            continue
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if method == "semantic":
            scores = compute_semantic_similarity_batch(citation_text, paragraphs, semantic_model)
            for para, cos_sim in zip(paragraphs, scores):
                if cos_sim >= similarity_threshold:
                    matches.append((page, para, float(cos_sim)))
        else:
            for paragraph in paragraphs:
                corpus = [citation_text, paragraph]
                vectorizer = TfidfVectorizer().fit(corpus)
                vectors = vectorizer.transform(corpus)
                cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
                if cos_sim >= similarity_threshold:
                    matches.append((page, paragraph, cos_sim))
        if progress_callback:
            progress_callback(idx + 1, total_pages)
    return matches
