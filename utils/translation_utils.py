import os
import dotenv
import deepl
from transformers import MarianMTModel, MarianTokenizer

dotenv.load_dotenv()

# Cache untuk local models
_local_models_cache = {}

def get_deepl_api_key():
    """Ambil API key DeepL dari environment variable."""
    key = os.getenv("DeepL_API_KEY")
    if not key:
        raise ValueError("DeepL_API_KEY belum diset. Pastikan environment variable DeepL_API_KEY sudah diset.")
    return key

def get_deepl_translator():
    """Inisialisasi translator dari library DeepL."""
    return deepl.Translator(get_deepl_api_key())

# Modified to accept model_name and use caching
def get_local_translation_model(model_name: str):
    """Inisialisasi atau ambil model lokal MarianMT dari cache."""
    if model_name in _local_models_cache:
        return _local_models_cache[model_name]
    
    # print(f"Loading local model: {model_name}...") # Untuk debugging/info
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    _local_models_cache[model_name] = (tokenizer, model)
    # print(f"Model {model_name} loaded and cached.")
    return tokenizer, model

# Modified to accept model_name
def translate_text_local(text: str, model_name: str):
    """Terjemahkan teks menggunakan model lokal MarianMT yang ditentukan."""
    tokenizer, model = get_local_translation_model(model_name)
    batch = tokenizer([text], return_tensors="pt", padding=True)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)

# Constants for local model names
LOCAL_MODEL_ID_EN = "Helsinki-NLP/opus-mt-id-en"
LOCAL_MODEL_EN_ID = "Helsinki-NLP/opus-mt-en-id"

def translate_text_from_ID_to_EN(text: str, use_local: bool = False):
    """
    Menerjemahkan teks dari Bahasa Indonesia ke Bahasa Inggris (EN-US)
    menggunakan DeepL API atau model lokal.
    """
    if use_local:
        try:
            return translate_text_local(text, LOCAL_MODEL_ID_EN)
        except Exception as e:
            # Spesifikasikan error untuk model lokal ID->EN
            raise RuntimeError(f"Terjadi error pada model lokal (ID->EN '{LOCAL_MODEL_ID_EN}'): {e}")
    try:
        translator = get_deepl_translator()
        result = translator.translate_text(text, source_lang="ID", target_lang="EN-US")
        return result.text
    except Exception as e:
        raise RuntimeError(f"Terjadi error pada DeepL API: {e}")

def translate_text_from_EN_to_ID(text: str, use_local: bool = False):
    """
    Menerjemahkan teks dari Bahasa Inggris ke Bahasa Indonesia
    menggunakan DeepL API atau model lokal.
    """
    if use_local:
        try:
            # Langsung gunakan fungsi translate_text_local dengan model yang benar
            return translate_text_local(text, LOCAL_MODEL_EN_ID)
        except Exception as e:
            # Spesifikasikan error untuk model lokal EN->ID
            raise RuntimeError(f"Terjadi error pada model lokal (EN->ID '{LOCAL_MODEL_EN_ID}'): {e}")
    try:
        translator = get_deepl_translator()
        result = translator.translate_text(text, source_lang="EN", target_lang="ID")
        return result.text
    except Exception as e:
        raise RuntimeError(f"Terjadi error pada DeepL API: {e}")
