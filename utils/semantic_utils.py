import nltk

try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError: # More specific exception for missing resource
    print("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)
except LookupError: # Fallback for older NLTK versions or other lookup issues
    print("NLTK 'punkt' tokenizer not found (LookupError). Downloading...")
    nltk.download('punkt', quiet=True)

def get_semantic_model():
    from sentence_transformers import SentenceTransformer
    """Inisialisasi model untuk representasi semantik (Sentence-BERT)."""
    return SentenceTransformer("paraphrase-MiniLM-L6-v2")

def compute_semantic_similarity(text1, text2, semantic_model=None):
    """
    Menghitung cosine similarity antara dua teks menggunakan
    model embedding Sentence-BERT.
    """
    if semantic_model is None:
        semantic_model = get_semantic_model()
    from sentence_transformers import util
    embedding1 = semantic_model.encode(text1, convert_to_tensor=True)
    embedding2 = semantic_model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

def compute_semantic_similarity_batch(query, candidates, semantic_model=None):
    """
    Compute cosine similarity between a query and a list of candidate texts using Sentence-BERT in batch.
    """
    if semantic_model is None:
        semantic_model = get_semantic_model()
    from sentence_transformers import util
    query_emb = semantic_model.encode([query], convert_to_tensor=True)
    candidates_emb = semantic_model.encode(candidates, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(query_emb, candidates_emb)[0].cpu().numpy()
    return scores
