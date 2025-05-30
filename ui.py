import streamlit as st
import os

def sidebar_settings():
    """
    Sidebar pengaturan aplikasi.
    Mengembalikan threshold, mode, method, use_local, sort_option.
    """
    st.header("Pengaturan")
    api_key = st.text_input("DeepL API Key", type="password", value=os.getenv("DeepL_API_KEY", ""))
    if api_key:
        os.environ["DeepL_API_KEY"] = api_key
    threshold = st.slider("Threshold Kemiripan", 0.0, 1.0, 0.6, 0.01)
    mode = st.radio("Mode Pemeriksaan", ["Kalimat", "Paragraf"])
    method = st.radio(
        "Metode Perbandingan",
        ["TF-IDF", "Semantic"],
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
    show_streamlit_header = st.checkbox("Tampilkan Header Streamlit (MainMenu/Deploy)", value=False)
    st.caption("Aplikasi ini responsif dan dapat digunakan di perangkat mobile maupun desktop.")
    # Atur visibilitas header Streamlit
    header_css = ""
    if not show_streamlit_header:
        header_css = "header[data-testid=\"stHeader\"] {display:none !important;}"
    st.markdown(f"<style>{header_css}</style>", unsafe_allow_html=True)
    return threshold, mode, method, use_local, sort_option

def show_matches(matches, tipe_cek, method, sort_option):
    """Tampilkan hasil pencocokan di UI."""
    st.subheader("Hasil Pencocokan")
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
