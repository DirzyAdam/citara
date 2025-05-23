import PyPDF2
import fitz  # PyMuPDF

def is_valid_pdf(filepath):
    """Validasi file PDF (bukan corrupt dan benar formatnya)."""
    try:
        with open(filepath, "rb") as f:
            PyPDF2.PdfReader(f)
        return True
    except Exception:
        return False

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

def highlight_matches_in_pdf(pdf_path, matches, output_path):
    """
    Highlight hasil pencocokan pada file PDF.
    matches: list of (page, text, similarity)
    """
    doc = fitz.open(pdf_path)
    for page_num, text, _ in matches:
        page = doc[page_num - 1]
        text_instances = page.search_for(text)
        for inst in text_instances:
            page.add_highlight_annot(inst)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
