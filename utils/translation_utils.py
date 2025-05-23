import os
import dotenv
import deepl
from transformers import MarianMTModel, MarianTokenizer

dotenv.load_dotenv()

def get_deepl_api_key():
    """Ambil API key DeepL dari environment variable."""
    key = os.getenv("DeepL_API_KEY")
    if not key:
        raise ValueError("DeepL_API_KEY belum diset. Pastikan environment variable DeepL_API_KEY sudah diset.")
    return key

def get_deepl_translator():
    """Inisialisasi translator dari library DeepL."""
    return deepl.Translator(get_deepl_api_key())

def get_local_translation_model():
    """Inisialisasi model lokal MarianMT."""
    LOCAL_MODEL_NAME = "Helsinki-NLP/opus-mt-id-en"
    tokenizer = MarianTokenizer.from_pretrained(LOCAL_MODEL_NAME)
    model = MarianMTModel.from_pretrained(LOCAL_MODEL_NAME)
    return tokenizer, model

def translate_text_local(text, tokenizer=None, model=None):
    """Terjemahkan teks Indonesia ke Inggris menggunakan model lokal MarianMT."""
    if tokenizer is None or model is None:
        tokenizer, model = get_local_translation_model()
    batch = tokenizer([text], return_tensors="pt", padding=True)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)

def translate_text_from_ID_to_EN(text, use_local=False):
    """
    Menerjemahkan teks dari Bahasa Indonesia ke Bahasa Inggris (EN-US)
    menggunakan DeepL API atau model lokal.
    """
    if use_local:
        tokenizer, model = get_local_translation_model()
        try:
            return translate_text_local(text, tokenizer, model)
        except Exception as e:
            raise RuntimeError(f"Terjadi error pada model lokal: {e}")
    try:
        translator = get_deepl_translator()
        result = translator.translate_text(text, source_lang="ID", target_lang="EN-US")
        return result.text
    except Exception as e:
        raise RuntimeError(f"Terjadi error pada DeepL API: {e}")

def translate_text_from_EN_to_ID(text, use_local=False):
    """
    Menerjemahkan teks dari Bahasa Inggris ke Bahasa Indonesia
    menggunakan DeepL API atau model lokal.
    """
    if use_local:
        tokenizer, model = get_local_translation_model()
        try:
            # MarianMT model untuk EN->ID: Helsinki-NLP/opus-mt-en-id
            from transformers import MarianMTModel, MarianTokenizer
            LOCAL_MODEL_NAME = "Helsinki-NLP/opus-mt-en-id"
            tokenizer = MarianTokenizer.from_pretrained(LOCAL_MODEL_NAME)
            model = MarianMTModel.from_pretrained(LOCAL_MODEL_NAME)
            batch = tokenizer([text], return_tensors="pt", padding=True)
            gen = model.generate(**batch)
            return tokenizer.decode(gen[0], skip_special_tokens=True)
        except Exception as e:
            raise RuntimeError(f"Terjadi error pada model lokal: {e}")
    try:
        translator = get_deepl_translator()
        result = translator.translate_text(text, source_lang="EN", target_lang="ID")
        return result.text
    except Exception as e:
        raise RuntimeError(f"Terjadi error pada DeepL API: {e}")
