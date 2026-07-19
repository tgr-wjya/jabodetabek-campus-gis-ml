# UAS SIG Ruang E-504: WebGIS & Machine Learning Suitability Selection

Repository ini berisi seluruh berkas proyek Ujian Akhir Semester (UAS) mata kuliah Sistem Informasi Geografis (SIG) Ruang E-504. Proyek ini mencakup pengembangan WebGIS interaktif serta pemodelan spasial Machine Learning (Random Forest) untuk merekomendasikan lokasi pembangunan kampus satelit baru di wilayah Jabodetabek dan Karawang.

## Detail Mahasiswa
*   **Nama Lengkap**: Tegar Wijaya Kusuma
*   **NIM**: 41523010217
*   **Program Studi**: Teknik Informatika
*   **Kelas / Ruang**: E-504
*   **Dosen Pengampu**: Mohamad Yusuf, S.Kom., M.Cs.

---

## 1. Soal 1: WebGIS Dashboard Aksesibilitas Kampus
Visualisasi dan analisis aksesibilitas multimoda transportasi massal (KRL/MRT/LRT dan TransJakarta) terhadap lokasi perguruan tinggi eksisting di Jabodetabek.

*   **Aplikasi Live**: [https://uas-gis-e504.streamlit.app/](https://uas-gis-e504.streamlit.app/)
*   **Kategori Aksesibilitas**:
    *   *Transit-Oriented* (Akses Baik): Kampus berjarak <= 1.000 meter dari stasiun kereta ATAU <= 500 meter dari halte TransJakarta.
    *   *Transit-Isolated* (Akses Buruk): Kampus di luar jangkauan kedua moda tersebut.
*   **Daftar Library**: Streamlit, Folium, Streamlit-Folium, Pandas, Numpy.

---

## 2. Soal 2: Model Prediksi Kelayakan Lokasi Kampus Satelit (Machine Learning)
Klasifikasi kesesuaian wilayah kecamatan untuk pembangunan kampus satelit baru menggunakan algoritma **Random Forest Classifier** (Akurasi: **85.00%**).

### Variabel Spasial (Feature Engineering):
1.  `dist_ind`: Jarak ke kawasan industri terdekat (Centroid Hub).
2.  `camp_dens`: Kepadatan kampus eksisting (jumlah kampus per km²).
3.  `toll_pct`: Panjang jalan tol yang memotong kecamatan dibagi luas kecamatan.
4.  `sma_grad`: Jumlah lulusan SMA per tahun (seeded proxy).
5.  `area_km2`: Luas wilayah kecamatan (km²).

### Urutan Feature Importance:
1.  `sma_grad` (Jumlah Lulusan SMA): **36.99%** (Paling Menentukan)
2.  `dist_ind` (Jarak ke Kawasan Industri): **31.10%**
3.  `toll_pct` (Akses Jalan Tol): **17.29%**
4.  `area_km2` (Luas Kecamatan): **10.52%**
5.  `camp_dens` (Kepadatan Kampus Eksisting): **4.09%**

---

## Struktur Direktori Proyek
```text
.
├── Project/
│   └── UAS.qgz                        # File Workspace QGIS Project
├── data_ready/
│   ├── Kecamatan_Jabodetabek.*        # Shapefile kecamatan yang sudah di-join variabel spasial
│   ├── Kawasan_Industri_Jabodetabek.* # Shapefile kawasan industri
│   ├── Akses_Jalan_Tol.*              # Shapefile rute jalan tol
│   ├── Sebaran_Kampus_Eksisting.*     # Shapefile titik koordinat kampus
│   ├── kecamatan_predictions.csv      # Hasil prediksi klasifikasi model ML
│   └── kecamatan_predictions_qgis.csv # Tabel prediksi hasil run script QGIS
├── app.py                             # Script aplikasi dashboard Streamlit WebGIS
├── calculate_spatial_features_qgis.py # Script Feature Engineering untuk dijalankan di QGIS Python Console
├── train_qgis.py                      # Script Random Forest untuk dijalankan di QGIS Python Console
├── requirements.txt                   # Daftar dependensi modul python untuk Streamlit Cloud
├── Laporan_UAS_GIS_E504.md            # Draf laporan akademik (Markdown)
├── Laporan_UAS_GIS_E504.docx          # Laporan akademik resmi (Word Document)
├── screenshot1.png                    # Screenshot visualisasi penuh WebGIS & legenda
├── screenshot2.png                    # Screenshot popup peta atribut kampus
├── README.md                          # Informasi umum repositori (file ini)
└── .gitignore                         # Konfigurasi pengecualian file pelacakan Git
```

---

## Petunjuk Penggunaan calculate_spatial_features_qgis.py di QGIS
Jika Anda ingin menghitung ulang seluruh variabel spasial (jarak kawasan industri, kepadatan kampus, dan persentase tol) dari awal menggunakan Python alih-alih menu GUI QGIS:
1.  Buka project **Project/UAS.qgz** di QGIS dan pastikan keempat layer spasial (`Kecamatan_Jabodetabek`, `Kawasan_Industri_Jabodetabek`, `Akses_Jalan_Tol`, `Sebaran_Kampus_Eksisting`) dimuat.
2.  Buka **Python Console** di QGIS (`Ctrl + Alt + P`).
3.  Buka berkas `calculate_spatial_features_qgis.py` di dalam editor QGIS tersebut.
4.  Klik tombol hijau **Run Script** (Play). Atribut spasial pada tabel layer `Kecamatan_Jabodetabek` akan dihitung dan diperbarui secara otomatis.

---

## Petunjuk Penggunaan train_qgis.py di QGIS
1.  Buka project **Project/UAS.qgz** di QGIS.
2.  Pastikan layer **`Kecamatan_Jabodetabek`** aktif (diklik/diseleksi di panel Layers).
3.  Buka **Python Console** di QGIS (`Plugins -> Python Console` atau tekan `Ctrl + Alt + P`).
4.  Klik tombol **Show Editor** (ikon kertas catatan pada toolbar konsol).
5.  Buka berkas `train_qgis.py` di dalam editor QGIS tersebut.
6.  Klik tombol hijau **Run Script** (tombol Play) untuk menjalankan pemodelan Random Forest dan mengekstrak matriks klasifikasi serta memicu pembuatan berkas CSV hasil prediksi di folder data Anda.
