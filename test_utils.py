import unittest
from utils.translation_utils import translate_text_from_ID_to_EN, translate_text_from_EN_to_ID
from utils.pdf_utils import extract_text_by_page, is_valid_pdf
from utils.semantic_utils import compute_semantic_similarity
from utils.similarity_utils import find_sentence_matches, find_paragraph_matches
from utils.docx_utils import extract_text_from_docx, extract_paragraphs_from_docx, extract_text_by_section
import os

class TestUtils(unittest.TestCase):
    """Unit test untuk berbagai fungsi utilitas Citara."""

    def test_translate_text_from_ID_to_EN(self):
        """Test terjemahan dari Bahasa Indonesia ke Bahasa Inggris menggunakan model lokal."""
        result = translate_text_from_ID_to_EN("Ini adalah tes.", use_local=True)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_translate_text_from_EN_to_ID(self):
        """Test terjemahan dari Bahasa Inggris ke Bahasa Indonesia menggunakan model lokal."""
        result = translate_text_from_EN_to_ID("This is a test.", use_local=True)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_is_valid_pdf(self):
        """Test validasi file PDF yang ada dan yang tidak ada."""
        pdf_path = "sample_pdf/Foundations of Large Language Models.pdf"
        if os.path.exists(pdf_path):
            self.assertTrue(is_valid_pdf(pdf_path))
        self.assertFalse(is_valid_pdf("tidak_ada.pdf"))

    def test_extract_text_by_page(self):
        """Test ekstraksi teks per halaman dari file PDF yang valid."""
        pdf_path = "sample_pdf/Foundations of Large Language Models.pdf"
        if os.path.exists(pdf_path):
            text = extract_text_by_page(pdf_path)
            self.assertIsInstance(text, dict)
            self.assertTrue(len(text) > 0)

    def test_compute_semantic_similarity(self):
        """Test kemiripan semantik antara dua string identik."""
        sim = compute_semantic_similarity("hello world", "hello world")
        self.assertGreaterEqual(sim, 0.9)

    def test_find_sentence_matches(self):
        """Test pencarian kemiripan kalimat menggunakan metode tfidf."""
        citation = "This is a test sentence."
        pages_text = {1: "This is a test sentence. Another sentence."}
        matches = find_sentence_matches(citation, pages_text, similarity_threshold=0.5, method="tfidf")
        self.assertTrue(len(matches) > 0)

    def test_find_paragraph_matches(self):
        """Test pencarian kemiripan paragraf menggunakan metode semantic."""
        citation = "This is a test paragraph."
        pages_text = {1: "This is a test paragraph. Another paragraph."}
        matches = find_paragraph_matches(citation, pages_text, similarity_threshold=0.5, method="semantic")
        self.assertTrue(len(matches) > 0)

    def test_extract_text_from_docx(self):
        """Test ekstraksi seluruh teks dari file docx."""
        docx_path = "sample_file/sample.docx"
        if os.path.exists(docx_path):
            text = extract_text_from_docx(docx_path)
            self.assertIsInstance(text, str)
            self.assertTrue(len(text) > 0)

    def test_extract_paragraphs_from_docx(self):
        """Test ekstraksi list paragraf dari file docx."""
        docx_path = "sample_file/sample.docx"
        if os.path.exists(docx_path):
            paragraphs = extract_paragraphs_from_docx(docx_path)
            self.assertIsInstance(paragraphs, list)
            self.assertTrue(all(isinstance(p, str) for p in paragraphs))

    def test_extract_text_by_section(self):
        """Test ekstraksi teks per section dari file docx."""
        docx_path = "sample_file/sample.docx"
        if os.path.exists(docx_path):
            section_text = extract_text_by_section(docx_path)
            self.assertIsInstance(section_text, dict)
            self.assertTrue(1 in section_text)

    def test_extract_text_by_page_error(self):
        """Test error handling pada ekstraksi teks PDF yang tidak ada."""
        text = extract_text_by_page("tidak_ada.pdf")
        self.assertIsInstance(text, dict)
        self.assertEqual(len(text), 0)

if __name__ == "__main__":
    unittest.main()
