# Citation Checker

Aplikasi sederhana untuk memeriksa kemiripan teks kutipan/paragraf dengan isi dokumen PDF. Aplikasi ini menggunakan model pembelajaran mesin untuk menghitung kesamaan teks dan mendukung terjemahan antar bahasa.

## Fitur Utama
- **Pemeriksaan Kutipan**: Periksa kesamaan teks kutipan/paragraf dengan dokumen PDF.
- **Dukungan Multi-Bahasa**: Terjemahkan teks antara Bahasa Indonesia dan Bahasa Inggris.
- **Ekstraksi Teks**: Ekstrak teks dari file PDF dan dokumen Word.
- **Antarmuka Pengguna**: Antarmuka berbasis web menggunakan Streamlit.

## Persiapan
1. Pastikan Anda sudah memasang Python 3.8+.
2. Buat virtual environment (opsional):
   ```
   python -m venv venv
   source venv/bin/activate  # atau venv\Scripts\activate di Windows
   ```
3. Install paket yang dibutuhkan:
   ```
   pip install -r requirements.txt
   ```

## Cara Menjalankan
1. Buka terminal di direktori project.
2. Jalankan Streamlit:
   ```
   streamlit run main.py
   ```
3. Akses aplikasi di browser sesuai alamat yang ditampilkan (biasanya http://localhost:8501).

## Struktur Proyek
```
1_citation-checker/
├── main.py                # File utama untuk menjalankan aplikasi
├── requirements.txt       # Daftar dependensi Python
├── utils/                 # Modul utilitas untuk PDF, Word, dan lainnya
│   ├── docx_utils.py      # Fungsi untuk memproses dokumen Word
│   ├── pdf_utils.py       # Fungsi untuk memproses file PDF
│   ├── semantic_utils.py  # Fungsi untuk analisis semantik
│   ├── similarity_utils.py# Fungsi untuk menghitung kesamaan teks
│   ├── translation_utils.py # Fungsi untuk terjemahan teks
├── sample_pdf/            # Contoh file PDF untuk pengujian
└── .streamlit/            # Konfigurasi Streamlit
```

## Kontribusi
Kontribusi sangat diterima! Silakan buat pull request atau laporkan masalah di [repository ini](#).

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).
