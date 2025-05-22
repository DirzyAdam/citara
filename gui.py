import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from utils import (
    translate_text_from_ID_to_EN,
    extract_text_by_page,
    find_sentence_matches,
    find_paragraph_matches
)

class CitationCheckerApp:
    def __init__(self, master):
        self.master = master
        # Set ukuran window dan latar belakang
        self.master.geometry("950x950")
        self.master.config(bg="white")
        self.master.title("Citation Checker")
        
        # Definisikan warna tema dan font
        self.primary_color = "#1E90FF"  # Dodger Blue
        self.secondary_color = "white"
        self.header_font = ("Helvetica", 13, "bold")
        self.normal_font = ("Helvetica", 11)
        
        self.frame = tk.Frame(master, bg="white")
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Label untuk teks sitasi
        tk.Label(self.frame, text="Teks Sitasi (Bahasa Indonesia):", bg="white",
                 fg=self.primary_color, font=self.header_font).grid(row=0, column=0, sticky="w")
        self.text_citation = tk.Text(self.frame, height=5, width=60, font=self.normal_font)
        self.text_citation.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Tombol untuk memilih file PDF
        self.btn_choose_file = tk.Button(
            self.frame, text="Pilih File PDF", command=self.choose_file,
            bg=self.primary_color, fg="white", font=self.normal_font
        )
        self.btn_choose_file.grid(row=2, column=0, sticky="w")
        self.label_pdf = tk.Label(self.frame, text="Tidak ada file yang dipilih", bg="white",
                                   fg=self.primary_color, font=self.normal_font)
        self.label_pdf.grid(row=2, column=1, columnspan=2, sticky="w")
        self.pdf_file_path = None

        # Entry untuk threshold kemiripan
        tk.Label(self.frame, text="Threshold Kemiripan:", bg="white",
                 fg=self.primary_color, font=self.header_font).grid(row=3, column=0, sticky="w")
        self.entry_threshold = tk.Entry(self.frame, width=10, font=self.normal_font)
        self.entry_threshold.insert(0, "0.6")
        self.entry_threshold.grid(row=3, column=1, sticky="w")

        # Pilihan mode pemeriksaan: Kalimat atau Paragraf
        tk.Label(self.frame, text="Mode Pemeriksaan:", bg="white",
                 fg=self.primary_color, font=self.header_font).grid(row=4, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="sentence")
        tk.Radiobutton(self.frame, text="Kalimat", variable=self.mode_var, value="sentence",
                       bg="white", fg=self.primary_color, font=self.normal_font).grid(row=4, column=1, sticky="w")
        tk.Radiobutton(self.frame, text="Paragraf", variable=self.mode_var, value="paragraph",
                       bg="white", fg=self.primary_color, font=self.normal_font).grid(row=4, column=2, sticky="w")

        # Pilihan metode perbandingan: TF-IDF atau Semantic
        tk.Label(self.frame, text="Metode Perbandingan:", bg="white",
                 fg=self.primary_color, font=self.header_font).grid(row=5, column=0, sticky="w")
        self.method_var = tk.StringVar(value="tfidf")
        tk.Radiobutton(self.frame, text="TF-IDF", variable=self.method_var, value="tfidf",
                       bg="white", fg=self.primary_color, font=self.normal_font).grid(row=5, column=1, sticky="w")
        tk.Radiobutton(self.frame, text="Semantic", variable=self.method_var, value="semantic",
                       bg="white", fg=self.primary_color, font=self.normal_font).grid(row=5, column=2, sticky="w")

        # Tombol proses
        self.btn_process = tk.Button(
            self.frame, text="Proses", command=self.process_data,
            bg=self.primary_color, fg="white", font=self.normal_font
        )
        self.btn_process.grid(row=6, column=0, pady=10)

        # Area output menggunakan widget scrolledtext
        self.output_text = scrolledtext.ScrolledText(self.frame, width=80, height=20, font=self.normal_font)
        self.output_text.grid(row=7, column=0, columnspan=3, pady=10)

    def choose_file(self):
        """Buka dialog untuk memilih file PDF."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_file_path = file_path
            self.label_pdf.config(text=os.path.basename(file_path))
        else:
            self.label_pdf.config(text="Tidak ada file yang dipilih")

    def process_data(self):
        """
        Ambil input dari widget, lakukan terjemahan teks, ekstraksi PDF, dan
        pencocokan (kalimat atau paragraf) lalu tampilkan hasil ke area output.
        """
        citation_text = self.text_citation.get("1.0", tk.END).strip()
        if not citation_text:
            messagebox.showwarning("Input Error", "Masukkan teks sitasi!")
            return

        try:
            threshold = float(self.entry_threshold.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Threshold harus berupa angka!")
            return

        mode = self.mode_var.get()      # "sentence" atau "paragraph"
        method = self.method_var.get()  # "tfidf" atau "semantic"

        if not self.pdf_file_path or not os.path.exists(self.pdf_file_path):
            messagebox.showwarning("Input Error", "Pilih file PDF referensi!")
            return

        # Bersihkan area output
        self.output_text.delete("1.0", tk.END)

        # Lakukan terjemahan teks sitasi
        try:
            translation = translate_text_from_ID_to_EN(citation_text)
        except Exception as e:
            self.output_text.insert(tk.END, "Error dalam menerjemahkan teks: " + str(e) + "\n")
            return

        self.output_text.insert(tk.END, f"Hasil back-translation: {translation}\n\n")

        # Ekstraksi teks dari file PDF
        pages_text = extract_text_by_page(self.pdf_file_path)
        if not pages_text:
            self.output_text.insert(tk.END, "Tidak dapat mengekstrak teks dari file PDF.\n")
            return

        # Cari kecocokan berdasarkan mode yang dipilih
        if mode == "paragraph":
            matches = find_paragraph_matches(translation, pages_text, similarity_threshold=threshold, method=method)
            tipe_cek = "Paragraf"
        else:
            matches = find_sentence_matches(translation, pages_text, similarity_threshold=threshold, method=method)
            tipe_cek = "Kalimat"

        # Tampilkan hasil pencocokan
        if matches:
            self.output_text.insert(tk.END, f"Ditemukan kemiripan pada {tipe_cek} (metode: {method}):\n")
            for page, text_match, sim in matches:
                self.output_text.insert(tk.END, f"Halaman {page}, Kemiripan: {sim:.2f}\nTeks:\n{text_match}\n\n{'-'*40}\n")
        else:
            self.output_text.insert(tk.END, f"Tidak ditemukan kemiripan signifikan pada {tipe_cek} dengan metode {method}.\n")