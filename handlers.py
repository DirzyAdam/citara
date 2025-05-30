import tempfile
import os
from utils.pdf_utils import is_valid_pdf

def process_pdf(uploaded_pdf):
    """Simpan file PDF upload ke file sementara dan kembalikan path-nya."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_pdf.read())
        return tmp_pdf.name

def validate_pdf(pdf_path, max_size_mb=20, max_pages=500):
    """Validasi ukuran dan jumlah halaman PDF."""
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)
    if file_size > max_size_mb:
        return False, f"Ukuran file PDF terlalu besar ({file_size:.1f} MB). Maksimal {max_size_mb} MB."
    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            if num_pages > max_pages:
                return False, f"Jumlah halaman PDF terlalu banyak ({num_pages}). Maksimal {max_pages} halaman."
        if not is_valid_pdf(pdf_path):
            return False, "File PDF tidak valid atau corrupt (berdasarkan pemeriksaan utils.pdf_utils)."
    except PyPDF2.errors.PdfReadError as e:
        return False, f"File PDF tidak dapat dibaca atau corrupt (PyPDF2 error: {e})."
    except Exception as e:
        return False, f"Terjadi error saat validasi PDF: {e}."
    return True, ""
