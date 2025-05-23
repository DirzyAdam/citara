import PyPDF2
import fitz  # PyMuPDF

def is_valid_pdf(filepath):
    """Validasi file PDF menggunakan PyMuPDF (fitz)."""
    doc = None  # Inisialisasi doc ke None
    try:
        doc = fitz.open(filepath)
        # Melakukan operasi dasar, misalnya cek jumlah halaman, bisa ditambahkan jika perlu
        # Untuk validasi dasar, pembukaan file saja sudah cukup untuk menangkap banyak error.
        return True
    except Exception: # Menangkap semua jenis exception yang mungkin terjadi saat membuka file
        return False
    finally:
        if doc:
            doc.close() # Pastikan dokumen ditutup jika berhasil dibuka

def extract_text_by_page(pdf_path):
    """
    Mengekstrak teks dari setiap halaman file PDF dan mengembalikannya
    sebagai dictionary dengan nomor halaman sebagai key.
    Menggunakan PyMuPDF (fitz) untuk ekstraksi yang lebih baik.
    """
    pages_text = {}
    try:
        doc = fitz.open(pdf_path)  # Menggunakan fitz untuk membuka PDF
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pages_text[page_num + 1] = page.get_text("text")
        doc.close()
        return pages_text
    except Exception as e:
        print(f"Error membaca file PDF dengan PyMuPDF: {e}")
        # Fallback ke PyPDF2 jika PyMuPDF gagal, atau hapus fallback jika tidak diinginkan
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
