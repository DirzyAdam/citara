import streamlit as st
from utils.translation_utils import translate_text_from_ID_to_EN
from utils.pdf_utils import extract_text_by_page, is_valid_pdf
from utils.similarity_utils import find_sentence_matches, find_paragraph_matches
import tempfile
import os

def sidebar_settings():
    st.header("Pengaturan")
    # Pengaturan API Key DeepL
    api_key = st.text_input("DeepL API Key", type="password", value=os.getenv("DeepL_API_KEY", ""))
    if api_key:
        os.environ["DeepL_API_KEY"] = api_key

    threshold = st.slider("Threshold Kemiripan", 0.0, 1.0, 0.6, 0.01)
    mode = st.radio("Mode Pemeriksaan", ["Kalimat", "Paragraf"])
    method = st.radio(
        "Metode Perbandingan",
        [
            "TF-IDF",
            "Semantic"
        ],
        index=1,
        help="TF-IDF (Term Frequency-Inverse Document Frequency) adalah metode statistik untuk menilai seberapa penting sebuah kata dalam dokumen relatif terhadap kumpulan dokumen lain.\n\nSemantic: Menggunakan model deep learning (Sentence-BERT) untuk memahami makna kalimat, cocok untuk kemiripan makna, bukan hanya kata."
    )
    use_local = st.checkbox("Gunakan Model Lokal (offline)", value=False)
    sort_option = st.radio(
        "Urutkan Hasil Berdasarkan",
        ["Tingkat Kemiripan (desc)", "Urutan Halaman (asc)"],
        index=0,
        help="Pilih cara pengurutan hasil pencocokan."
    )
    st.caption("Aplikasi ini responsif dan dapat digunakan di perangkat mobile maupun desktop.")
    return threshold, mode, method, use_local, sort_option

def process_pdf(uploaded_pdf):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_pdf.read())
        pdf_path = tmp_pdf.name
    return pdf_path

def show_matches(matches, tipe_cek, method, sort_option):
    st.subheader("Hasil Pencocokan")
    # Sorting
    if sort_option == "Tingkat Kemiripan (desc)":
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
    else:
        matches = sorted(matches, key=lambda x: x[0])
    if matches:
        st.success(f"Ditemukan kemiripan pada {tipe_cek} (metode: {method}):")
        for page, text_match, sim in matches:
            st.markdown(
                f"""
                <div style="background-color:#eaf3fb; border-left:5px solid #1E90FF; padding:10px; margin-bottom:10px;">
                <b>Halaman {page}</b> &nbsp; | &nbsp; <b>Kemiripan:</b> <span style="color:#1E90FF;">{sim:.2f}</span><br>
                <span style="color:#222;">{text_match}</span>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.info(f"Tidak ditemukan kemiripan signifikan pada {tipe_cek} dengan metode {method}.")

def validate_pdf(pdf_path, max_size_mb=20, max_pages=500):
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
    except Exception:
        return False, "File PDF tidak valid atau corrupt."
    return True, ""

def run_app():
    st.set_page_config(page_title="Citation Checker", layout="wide", page_icon="🔎")
    st.markdown(
        """
        <style>
        .main {background-color: #ffffff;}
        .stTextArea textarea {background-color: #ffffff !important; color: #1E2A40 !important;}
        .stTextInput input {background-color: #ffffff !important; color: #1E2A40 !important;}
        .stButton>button {
            background-color: #1E90FF;
            color: #ffffff;
            border-radius: 6px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #1565c0;
            color: #ffffff;
        }
        .stFileUploader {background-color: #ffffff;}
        .stApp {background-color: #ffffff;}
        </style>
        """, unsafe_allow_html=True
    )

    st.title("🔎 Citation Checker")
    st.markdown(
        "<h3 style='color:#1E90FF;'>Cek kemiripan kutipan/paragraf dengan sumber PDF secara otomatis.</h3>",
        unsafe_allow_html=True
    )

    with st.sidebar:
        threshold, mode, method, use_local, sort_option = sidebar_settings()

    st.subheader("Teks Sitasi")
    # Pilihan bahasa untuk input sitasi (user)
    lang_options = {"Bahasa Indonesia": "ID", "Bahasa Inggris": "EN"}
    citation_lang = st.selectbox("Bahasa Teks Sitasi", list(lang_options.keys()), index=0)
    citation_text = st.text_area("Masukkan teks sitasi", height=120, key="citation_input")

    st.subheader("Upload File PDF Sumber")
    # Pilihan bahasa untuk PDF sumber
    source_lang = st.selectbox("Bahasa Sumber PDF", list(lang_options.keys()), index=0, key="pdf_source_lang")
    uploaded_pdf = st.file_uploader("Pilih file PDF", type=["pdf"])

    process = st.button("Proses")

    if process:
        if not citation_text.strip():
            st.warning("Masukkan teks sitasi!")
        elif not uploaded_pdf:
            st.warning("Pilih file PDF referensi!")
        else:
            with st.spinner("Menerjemahkan dan memproses..."):
                pdf_path = process_pdf(uploaded_pdf)
                # Validasi ukuran dan halaman PDF
                valid, msg = validate_pdf(pdf_path)
                if not valid:
                    st.error(msg)
                    os.unlink(pdf_path)
                    st.stop()
                if not is_valid_pdf(pdf_path):
                    st.error("File PDF tidak valid atau corrupt.")
                    os.unlink(pdf_path)
                    st.stop()

                pages_text = extract_text_by_page(pdf_path)
                if not pages_text:
                    st.error("Tidak dapat mengekstrak teks dari file PDF.")
                    os.unlink(pdf_path)
                    st.stop()

                # Deteksi bahasa sumber dan target, lakukan translasi jika perlu
                citation_for_compare = citation_text
                translation_info = ""
                citation_lang_code = lang_options[citation_lang]
                source_lang_code = lang_options[source_lang]
                if citation_lang_code != source_lang_code:
                    try:
                        if citation_lang_code == "ID" and source_lang_code == "EN":
                            citation_for_compare = translate_text_from_ID_to_EN(citation_text, use_local=use_local)
                            translation_info = f"(Sitasi diterjemahkan dari Bahasa Indonesia ke Bahasa Inggris)"
                        elif citation_lang_code == "EN" and source_lang_code == "ID":
                            from utils.translation_utils import translate_text_from_EN_to_ID
                            citation_for_compare = translate_text_from_EN_to_ID(citation_text, use_local=use_local)
                            translation_info = f"(Sitasi diterjemahkan dari Bahasa Inggris ke Bahasa Indonesia)"
                    except Exception as e:
                        st.error(f"Error dalam menerjemahkan sitasi: {e}")
                        os.unlink(pdf_path)
                        st.stop()
                else:
                    translation_info = "(Tidak perlu translasi, bahasa sama)"

                st.info(f"**Sitasi yang digunakan untuk pencocokan:** {citation_for_compare}\n\n{translation_info}")

                # Optimasi performa: warning untuk PDF besar
                if len(pages_text) > 100:
                    st.warning("PDF ini cukup besar, proses bisa memakan waktu lebih lama dari biasanya.")

                progress_text = "Memproses kemiripan..."
                progress_bar = st.progress(0, text=progress_text)
                def progress_callback(val, maxval):
                    progress_bar.progress(val / maxval, text=f"{progress_text} ({val}/{maxval} halaman)")

                if mode == "Paragraf":
                    matches = find_paragraph_matches(
                        citation_for_compare, pages_text, similarity_threshold=threshold,
                        method=method.lower(), progress_callback=progress_callback
                    )
                    tipe_cek = "Paragraf"
                else:
                    matches = find_sentence_matches(
                        citation_for_compare, pages_text, similarity_threshold=threshold,
                        method=method.lower(), progress_callback=progress_callback
                    )
                    tipe_cek = "Kalimat"
                progress_bar.empty()

                os.unlink(pdf_path)
                show_matches(matches, tipe_cek, method, sort_option)

    # Unit test tetap di file terpisah (test_utils.py), pastikan semua fungsi modular sudah diuji.

if __name__ == "__main__":
    run_app()