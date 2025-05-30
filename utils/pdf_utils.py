import PyPDF2
import fitz

def is_valid_pdf(filepath):
    """Validasi file PDF menggunakan PyMuPDF (fitz)."""
    doc = None
    try:
        doc = fitz.open(filepath)
        return True
    except Exception:
        return False
    finally:
        if doc:
            doc.close()

def extract_text_by_page(pdf_path):
    """
    Mengekstrak teks dari setiap halaman file PDF dan mengembalikannya
    sebagai dictionary dengan nomor halaman sebagai key.
    Menggunakan PyMuPDF (fitz) untuk ekstraksi yang lebih baik.
    """
    pages_text = {}
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pages_text[page_num + 1] = page.get_text("text")
        doc.close()
        return pages_text
    except Exception as e:
        print(f"Error membaca file PDF dengan PyMuPDF: {e}")
        print("Mencoba dengan PyPDF2 sebagai fallback...")
        try:
            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    pages_text[page_num + 1] = page_text
            return pages_text
        except Exception as e2:
            print(f"Error membaca file PDF dengan PyPDF2: {e2}")
            return {}

def highlight_matches_in_pdf(pdf_path, matches, output_path):
    """
    Highlight hasil pencocokan pada file PDF.
    
    Parameters:
    - pdf_path: str, path ke file PDF sumber.
    - matches: list of tuples, setiap tuple berisi (nomor_halaman, teks, kesamaan).
    - output_path: str, path untuk menyimpan file PDF yang sudah di-highlight.
    """
    doc = fitz.open(pdf_path)
    for page_num, text, _ in matches:
        page = doc[page_num - 1]
        text_instances = page.search_for(text)
        for inst in text_instances:
            page.add_highlight_annot(inst)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
