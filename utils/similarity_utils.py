import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.semantic_utils import get_semantic_model, compute_semantic_similarity, compute_semantic_similarity_batch
import concurrent.futures

def _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, text_splitter_func):
    """
    Fungsi generik untuk mencari kemiripan antara citation_text dan setiap unit (kalimat/paragraf) pada pages_text.
    """
    matches = []
    total_pages = len(pages_text)
    semantic_model = None
    if method == "semantic":
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
    Gabungan metode:
    1. Gabungkan baris yang terputus (line wrapping)
    2. Gunakan NLTK sent_tokenize
    3. Fallback ke regex jika NLTK gagal
    4. (Opsional) Gunakan blok layout PyMuPDF jika value sudah list (hasil blok)
    """
    import re
    def robust_sentence_splitter(text_content):
        # Jika value sudah list (misal hasil blok layout), gabungkan lalu proses per blok
        if isinstance(text_content, list):
            sentences = []
            for block in text_content:
                sentences.extend(robust_sentence_splitter(block))
            return sentences
        # Gabungkan baris yang terputus (line wrapping)
        lines = text_content.split('\n')
        joined = ""
        for line in lines:
            line = line.strip()
            if not line:
                joined += "\n"
                continue
            # Jika baris kemungkinan judul/subjudul (huruf besar semua, atau panjang < 80 dan tidak diakhiri tanda baca)
            if (len(line) < 80 and not re.search(r'[.!?…:;\"”\']$', line) and
                (line.isupper() or line.istitle() or re.match(r'^[A-Z][A-Z\s\-0-9]+$', line))):
                if joined:
                    joined += "\n"
                joined += line + "\n"  # Pisahkan judul/subjudul sebagai paragraf/kalimat sendiri
                continue
            if joined and not re.search(r'[.!?…:;\"”\']$', joined.strip()):
                joined += ' ' + line
            else:
                joined += '\n' + line
        # Tokenisasi kalimat per paragraf
        sentences = []
        for para in joined.split('\n'):
            para = para.strip()
            if para:
                # Jika kemungkinan judul/subjudul, masukkan langsung
                if (len(para) < 80 and not re.search(r'[.!?…:;\"”\']$', para) and
                    (para.isupper() or para.istitle() or re.match(r'^[A-Z][A-Z\s\-0-9]+$', para))):
                    sentences.append(para)
                else:
                    try:
                        sentences.extend(nltk.tokenize.sent_tokenize(para))
                    except Exception:
                        # Fallback ke regex jika NLTK gagal
                        sentences.extend([s.strip() for s in re.split(r'(?<=[.!?])\s+', para) if s.strip()])
        return [s.strip() for s in sentences if s.strip()]
    return _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, robust_sentence_splitter)

def find_paragraph_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None):
    """
    Mencari kemiripan paragraf. Jika value sudah list (hasil extract_paragraphs_by_page), gunakan langsung,
    jika string, split dengan dua baris baru/baris kosong.
    """
    def paragraph_splitter(text_content):
        import re
        if isinstance(text_content, list):
            return [p.strip() for p in text_content if p.strip()]
        return [p.strip() for p in re.split(r'\n\s*\n', text_content) if p.strip()]
    return _find_matches_generic(citation_text, pages_text, similarity_threshold, method, progress_callback, paragraph_splitter)

def find_crossunit_matches(citation_text, pages_text, similarity_threshold=0.6, method="tfidf", progress_callback=None, window_size=3, unit_mode="paragraph"):
    """
    Mencari kemiripan sitasi dengan gabungan beberapa unit (paragraf/kalimat) secara sliding window.
    - window_size: jumlah unit yang digabungkan per window.
    - unit_mode: "paragraph" atau "sentence".
    Returns: list of (page, gabungan_unit, skor)
    """
    import re
    from itertools import chain
    matches = []
    total_pages = len(pages_text)
    semantic_model = None
    if method == "semantic":
        semantic_model = get_semantic_model()
    vectorizer = None
    if method == "tfidf":
        vectorizer = TfidfVectorizer()

    def process_page(args):
        idx, page, text = args
        # Pilih splitter sesuai mode
        if unit_mode == "sentence":
            def splitter(txt):
                def robust_sentence_splitter(text_content):
                    if isinstance(text_content, list):
                        sentences = []
                        for block in text_content:
                            sentences.extend(robust_sentence_splitter(block))
                        return sentences
                    lines = text_content.split('\n')
                    joined = ""
                    for line in lines:
                        line = line.strip()
                        if not line:
                            joined += "\n"
                            continue
                        if (len(line) < 80 and not re.search(r'[.!?…:;\"”\']$', line) and
                            (line.isupper() or line.istitle() or re.match(r'^[A-Z][A-Z\s\-0-9]+$', line))):
                            if joined:
                                joined += "\n"
                            joined += line + "\n"
                            continue
                        if joined and not re.search(r'[.!?…:;\"”\']$', joined.strip()):
                            joined += ' ' + line
                        else:
                            joined += '\n' + line
                    sentences = []
                    for para in joined.split('\n'):
                        para = para.strip()
                        if para:
                            if (len(para) < 80 and not re.search(r'[.!?…:;\"”\']$', para) and
                                (para.isupper() or para.istitle() or re.match(r'^[A-Z][A-Z\s\-0-9]+$', para))):
                                sentences.append(para)
                            else:
                                try:
                                    sentences.extend(nltk.tokenize.sent_tokenize(para))
                                except Exception:
                                    sentences.extend([s.strip() for s in re.split(r'(?<=[.!?])\s+', para) if s.strip()])
                    return [s.strip() for s in sentences if s.strip()]
                return robust_sentence_splitter(txt)
        else:
            def splitter(txt):
                if isinstance(txt, list):
                    return [p.strip() for p in txt if p.strip()]
                return [p.strip() for p in re.split(r'\n\s*\n', txt) if p.strip()]
        units = splitter(text)
        if not units or len(units) < window_size:
            return []
        # Sliding window
        window_texts = [" ".join(units[i:i+window_size]) for i in range(len(units) - window_size + 1)]
        results = []
        if method == "semantic":
            # Batch processing
            scores = compute_semantic_similarity_batch(citation_text, window_texts, semantic_model)
            for window_text, score in zip(window_texts, scores):
                if score >= similarity_threshold:
                    results.append((page, window_text, float(score)))
        else:
            for window_text in window_texts:
                if vectorizer is None:
                    local_vectorizer = TfidfVectorizer()
                else:
                    local_vectorizer = vectorizer
                corpus = [citation_text, window_text]
                vectors = local_vectorizer.fit_transform(corpus)
                cos_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                if cos_sim >= similarity_threshold:
                    results.append((page, window_text, cos_sim))
        return results

    # Parallel processing per halaman
    with concurrent.futures.ThreadPoolExecutor() as executor:
        args_list = [(idx, page, text) for idx, (page, text) in enumerate(pages_text.items())]
        future_to_idx = {executor.submit(process_page, args): args[0] for args in args_list}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_idx)):
            page_results = future.result()
            matches.extend(page_results)
            if progress_callback:
                progress_callback(i + 1, total_pages)
    return matches
