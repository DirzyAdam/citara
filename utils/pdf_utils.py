import PyPDF2
import fitz
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_pdf(filepath):
    """Validasi file PDF menggunakan PyMuPDF (fitz)."""
    doc = None
    try:
        doc = fitz.open(filepath)
        if doc.page_count > 0:
            return True
        return False
    except Exception as e:
        logging.error(f"Gagal memvalidasi PDF {filepath}: {e}")
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
    doc = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            pages_text[page_num + 1] = text
        return pages_text
    except Exception as e:
        logging.error(f"Error membaca file PDF dengan PyMuPDF: {e}")
        logging.info("Mencoba dengan PyPDF2 sebagai fallback...")
        try:
            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for i, p_reader in enumerate(pdf_reader.pages):
                    page_text_fallback = p_reader.extract_text()
                    pages_text[i + 1] = page_text_fallback if page_text_fallback else ""
            return pages_text
        except Exception as e2:
            logging.error(f"Error membaca file PDF dengan PyPDF2: {e2}")
            return {}
    finally:
        if doc:
            doc.close()

def highlight_matches_in_pdf(pdf_path, matches, output_path):
    """
    Highlight hasil pencocokan pada file PDF.
    matches: list of (page_number, text_segment, similarity_score)
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        for page_num, text_segment, _ in matches:
            if page_num > len(doc) or page_num < 1:
                logging.warning(f"Nomor halaman tidak valid ({page_num}) untuk highlight. Dilewati.")
                continue
            page = doc.load_page(page_num - 1)
            text_instances = page.search_for(text_segment)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.update()
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        logging.info(f"PDF dengan highlight disimpan ke: {output_path}")
    except Exception as e:
        logging.error(f"Error saat membuat highlight di PDF {pdf_path}: {e}")
    finally:
        if doc:
            doc.close()

def extract_paragraphs_by_page(pdf_path):
    """
    Mengekstrak paragraf dari setiap halaman file PDF menggunakan PyMuPDF (fitz).
    Gabungan metode:
    1. Gunakan blok layout PyMuPDF (fitz) jika blok cukup panjang (bukan header/footer/nomor halaman).
    2. Jika blok terlalu panjang, split dengan dua baris baru/baris kosong ATAU indentasi awal baris.
    3. Gabungkan baris yang terputus (line wrapping) dalam satu paragraf.
    Returns: dict {page_number: [paragraf, ...]}
    """
    import re
    paragraphs_per_page = {}
    doc = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")
            paras = []
            for b in blocks:
                block_text = b[4].strip()
                # Filter blok yang sangat pendek (kemungkinan header/footer/nomor halaman)
                if not block_text or len(block_text) < 20:
                    continue
                # Jika blok sudah cukup pendek (misal < 600 karakter), anggap satu paragraf
                if len(block_text) < 600:
                    paras.append(block_text)
                else:
                    # Split dengan dua baris baru ATAU indentasi awal baris
                    split_paras = re.split(r'(?:\n\s*\n)|(?:\n[ \t]+)', block_text)
                    for para in split_paras:
                        para = para.strip()
                        if not para:
                            continue
                        # Gabungkan baris yang terputus (line wrapping)
                        lines = para.split('\n')
                        joined = ""
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if joined and not joined.endswith(('.', '!', '?', ':')):
                                joined += ' ' + line
                            else:
                                if joined:
                                    paras.append(joined.strip())
                                joined = line
                        if joined:
                            paras.append(joined.strip())
            paragraphs_per_page[page_num + 1] = [p for p in paras if p.strip()]
        return paragraphs_per_page
    except Exception as e:
        logging.error(f"Error ekstraksi paragraf PDF dengan PyMuPDF: {e}")
        return {}
    finally:
        if doc:
            doc.close()
