from ui import sidebar_settings, show_matches
from handlers import process_pdf, validate_pdf
import streamlit as st
from utils.translation_utils import translate_text_from_ID_to_EN, translate_text_from_EN_to_ID
from utils.pdf_utils import extract_text_by_page
from utils.similarity_utils import find_sentence_matches, find_paragraph_matches, find_crossunit_matches
from utils.docx_utils import extract_text_from_docx
import os

def run_app():
    st.set_page_config(page_title="Citara", layout="wide", page_icon="assets/logo-c.PNG")

    # --- SIDEBAR ---
    with st.sidebar:
        threshold, mode, method, use_local, sort_option = sidebar_settings()
        # Tambahkan pengaturan untuk mode rangkuman/lintas section
        crossunit_mode = st.checkbox(
            "Mode Rangkuman/Lintas Section",
            value=False,
            help="Aktifkan fitur ini untuk mendeteksi sitasi yang merupakan rangkuman/gabungan dari beberapa kalimat atau paragraf di sumber (sliding window). Cocok untuk sitasi berupa kesimpulan atau parafrase lintas bagian dokumen."
        )
        if crossunit_mode:
            window_size = st.slider("Ukuran Window Gabungan (unit)", 2, 6, 3)
            unit_mode = st.radio("Unit Gabungan", ["Kalimat", "Paragraf"], index=0)

    # --- MAIN LAYOUT ---
    st.markdown("""
        <style>
        /* Perkecil padding konten utama agar lebih rapat dan efisien */
        .main .block-container {
            padding-top: 0.3rem !important;
            padding-bottom: 1.2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
        /* Perkecil padding horizontal dan atas khusus untuk .st-emotion-cache-zy6yx3 */
        .st-emotion-cache-zy6yx3 {
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
            padding-top: 1.2rem !important;
        }
        /* Logo Citara di tengah layar */
        .citara-logo-center {
            display: flex;
            justify-content: center !important;
            align-items: center;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 10px;
            padding-left: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class='citara-logo-center'>
            <div style='display: flex; justify-content: center; align-items: center; width: 100%;'>
                <div style='max-width:60vw;'>
    """, unsafe_allow_html=True)
    import pathlib
    logo_svg = pathlib.Path("assets/logo-citara.svg")
    logo_png = pathlib.Path("assets/logo-citara.PNG")
    if logo_svg.exists():
        with open(logo_svg, "r", encoding="utf-8") as f:
            svg_content = f.read()
        # Tambahkan style langsung ke SVG agar width dan height sedikit lebih besar (misal 80px)
        import re
        svg_content = re.sub(r'<svg([^>]*)>', r'<svg\1 width="80" height="80">', svg_content, count=1)
        st.markdown(svg_content, unsafe_allow_html=True)
    else:
        st.image(str(logo_png), use_container_width=False, width=80)
    st.markdown("""
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h3 style='color:#1E90FF;text-align:center;'>Cek kemiripan kutipan/paragraf dengan sumber PDF/DOCX secara otomatis.</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("Teks Sitasi")
        lang_options = {"Bahasa Indonesia": "ID", "Bahasa Inggris": "EN"}
        # Hilangkan margin bawah pada selectbox agar label textarea dan file uploader sejajar
        st.markdown("""
        <style>
        div[data-baseweb='select'] > div {
            margin-bottom: 0 !important;
        }
        .stTextArea textarea#citation_input {
            width: 100% !important;
            min-width: 48vw !important;
            max-width: 100vw !important;
            min-height: 120px !important;
            max-height: 60vh !important;
            height: auto !important;
            font-size: 1.1rem;
            resize: vertical !important;
        }
        /* Samakan posisi y label input sitasi dan file uploader */
        .stTextArea label[for='citation_input'] {
            margin-bottom: 0.5rem !important;
            display: block;
        }
        .stFileUploader label[for='pdf_source_lang'] {
            margin-bottom: 0.5rem !important;
            display: block;
        }
        .stFileUploader label[for^='file_uploader'] {
            margin-top: 2.2rem !important;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)
        citation_lang = st.selectbox("Bahasa Teks Sitasi", list(lang_options.keys()), index=0)
        citation_text = st.text_area("Masukkan teks sitasi", height=None, key="citation_input")
    with col2:
        st.subheader("Upload File Sumber")
        # Hilangkan margin bawah pada selectbox dan file_uploader agar label sejajar dan komponen lebih rapat
        st.markdown("""
        <style>
        div[data-baseweb='select'] > div {
            margin-bottom: 0 !important;
        }
        .stFileUploader label[for^='file_uploader'] {
            margin-bottom: 0.5rem !important;
            margin-top: 0 !important;
            display: block;
        }
        .stFileUploader div[data-testid='stFileUploaderDropzone'] {
            margin-top: 0.5rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        source_lang = st.selectbox("Bahasa Sumber", list(lang_options.keys()), index=0, key="pdf_source_lang")
        uploaded_source = st.file_uploader("Pilih file sumber (PDF atau Word)", type=["pdf", "docx"])
        process = st.button("Proses", use_container_width=True, key="btn-proses")
        st.markdown("""
        <style>
        div[data-testid='stButton'] button#btn-proses {
            background-color: #1E90FF !important;
            color: white !important;
            font-size: 0.95rem !important;
            padding: 0.35rem 1.2rem !important;
            border-radius: 6px !important;
            border: none !important;
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
            float: right !important;
            box-shadow: 0 2px 8px rgba(30,144,255,0.08);
            transition: background 0.2s;
        }
        div[data-testid='stButton'] button#btn-proses:hover {
            background-color: #156ec0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if process:
        if not citation_text.strip():
            st.warning("Masukkan teks sitasi!")
        elif not uploaded_source:
            st.warning("Pilih file sumber (PDF/Word)!")
        else:
            with st.spinner("Menerjemahkan dan memproses..."):
                file_ext = os.path.splitext(uploaded_source.name)[1].lower()
                if file_ext == ".pdf":
                    source_path = process_pdf(uploaded_source)
                    valid, msg = validate_pdf(source_path)
                    if not valid:
                        st.error(msg)
                        os.unlink(source_path)
                        st.stop()
                    if mode == "Paragraf":
                        from utils.pdf_utils import extract_paragraphs_by_page
                        pages_text = extract_paragraphs_by_page(source_path)  # dict {halaman: [paragraf, ...]}
                    else:
                        pages_text = extract_text_by_page(source_path)
                    if not pages_text:
                        st.error("Tidak dapat mengekstrak teks dari file PDF.")
                        os.unlink(source_path)
                        st.stop()
                elif file_ext == ".docx":
                    try:
                        text = extract_text_from_docx(uploaded_source)
                        pages_text = {1: text}
                        source_path = None
                    except Exception as e:
                        st.error(f"Gagal membaca file Word: {e}")
                        st.stop()
                else:
                    st.error("Format file sumber tidak didukung. Hanya PDF dan Word (.docx).")
                    st.stop()

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
                            citation_for_compare = translate_text_from_EN_to_ID(citation_text, use_local=use_local)
                            translation_info = f"(Sitasi diterjemahkan dari Bahasa Inggris ke Bahasa Indonesia)"
                    except Exception as e:
                        st.error(f"Error dalam menerjemahkan sitasi: {e}")
                        if file_ext == ".pdf" and source_path:
                            os.unlink(source_path)
                        st.stop()
                else:
                    translation_info = "(Tidak perlu translasi, bahasa sama)"

                st.info(f"**Sitasi yang digunakan untuk pencocokan:** {citation_for_compare}\n\n{translation_info}")

                if len(pages_text) > 100:
                    st.warning("File sumber ini cukup besar, proses bisa memakan waktu lebih lama dari biasanya.")

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
                elif 'crossunit_mode' in locals() and crossunit_mode:
                    matches = find_crossunit_matches(
                        citation_for_compare, pages_text, similarity_threshold=threshold,
                        method=method.lower(), progress_callback=progress_callback,
                        window_size=window_size, unit_mode="sentence" if unit_mode=="Kalimat" else "paragraph"
                    )
                    tipe_cek = f"Gabungan {window_size} {unit_mode.lower()}"
                else:
                    matches = find_sentence_matches(
                        citation_for_compare, pages_text, similarity_threshold=threshold,
                        method=method.lower(), progress_callback=progress_callback
                    )
                    tipe_cek = "Kalimat"
                progress_bar.empty()

                if file_ext == ".pdf" and source_path:
                    os.unlink(source_path)
                show_matches(matches, tipe_cek, method, sort_option)

if __name__ == "__main__":
    run_app()