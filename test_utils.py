import unittest
from utils.translation_utils import translate_text_from_ID_to_EN
from utils.pdf_utils import extract_text_by_page, is_valid_pdf
from utils.semantic_utils import compute_semantic_similarity

class TestUtils(unittest.TestCase):
    def test_translate_text_from_ID_to_EN(self):
        result = translate_text_from_ID_to_EN("Ini adalah tes.", use_local=True)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_is_valid_pdf(self):
        self.assertTrue(is_valid_pdf("sample_pdf/Foundations of Large Language Models.pdf"))  # Ganti dengan path PDF valid
        self.assertFalse(is_valid_pdf("tidak_ada.pdf"))

    def test_compute_semantic_similarity(self):
        sim = compute_semantic_similarity("hello world", "hello world")
        self.assertGreaterEqual(sim, 0.9)

if __name__ == "__main__":
    unittest.main()
