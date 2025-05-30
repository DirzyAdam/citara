import unittest
from utils.translation_utils import translate_text_from_ID_to_EN, translate_text_from_EN_to_ID
from utils.pdf_utils import extract_text_by_page, is_valid_pdf
from utils.semantic_utils import compute_semantic_similarity
from utils.similarity_utils import find_sentence_matches, find_paragraph_matches
from utils.docx_utils import extract_text_from_docx
import os

class TestUtils(unittest.TestCase):
    def test_translate_text_from_ID_to_EN(self):
        result = translate_text_from_ID_to_EN("Ini adalah tes.", use_local=True)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_translate_text_from_EN_to_ID(self):
        result = translate_text_from_EN_to_ID("This is a test.", use_local=True)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_is_valid_pdf(self):
        self.assertTrue(is_valid_pdf("sample_file/Foundations of Large Language Models.pdf"))  # Ganti dengan path PDF valid
        self.assertFalse(is_valid_pdf("tidak_ada.pdf"))

    def test_extract_text_by_page(self):
        text = extract_text_by_page("sample_file/Foundations of Large Language Models.pdf")
        self.assertIsInstance(text, dict)
        self.assertTrue(len(text) > 0)

    def test_compute_semantic_similarity(self):
        sim = compute_semantic_similarity("hello world", "hello world")
        self.assertGreaterEqual(sim, 0.9)

    def test_find_sentence_matches(self):
        citation = "This is a test sentence."
        pages_text = {1: "This is a test sentence. Another sentence."}
        matches = find_sentence_matches(citation, pages_text, similarity_threshold=0.5, method="tf-idf")
        self.assertTrue(len(matches) > 0)

    def test_find_paragraph_matches(self):
        citation = "This is a test paragraph."
        pages_text = {1: "This is a test paragraph. Another paragraph."}
        matches = find_paragraph_matches(citation, pages_text, similarity_threshold=0.5, method="semantic")
        self.assertTrue(len(matches) > 0)

    def test_extract_text_from_docx(self):
        # Pastikan ada file Word valid untuk pengujian
        docx_path = "sample_file/sample.docx"  # Ganti dengan path file Word valid
        if os.path.exists(docx_path):
            text = extract_text_from_docx(docx_path)
            self.assertIsInstance(text, str)
            self.assertTrue(len(text) > 0)

if __name__ == "__main__":
    unittest.main()
