# UAS SIG Ruang E-504: WebGIS & Machine Learning Suitability Selection

Repository ini berisi seluruh berkas proyek Ujian Akhir Semester (UAS) mata kuliah Sistem Informasi Geografis (SIG) Ruang E-504. Proyek ini mencakup pengembangan **WebGIS Interaktif Multi-Tab berbasis Streamlit** serta pemodelan spasial Machine Learning (Random Forest) untuk merekomendasikan lokasi pembangunan kampus satelit baru di wilayah Jabodetabek dan Karawang.

## Detail Mahasiswa & Informasi Akademik
* **Nama Lengkap**: Tegar Wijaya Kusuma
* **NIM**: 41523010217
* **Program Studi**: Teknik Informatika / Fakultas Ilmu Komputer
* **Kelas / Ruang**: E-504
* **Dosen Pengampu**: Mohamad Yusuf, S.Kom., M.Cs.
* **Live WebGIS Dashboard**: [https://uas-gis-e504.streamlit.app/](https://uas-gis-e504.streamlit.app/)

---

## Modul Utama WebGIS Dashboard (`app.py`)

Aplikasi dikembangkan secara responsif dan ringan dalam **100% Bahasa Indonesia** menggunakan dua tab utama:

### 1. Tab 1: Peta Aksesibilitas Transportasi Massal Perguruan Tinggi (Soal 1)
* **Visualisasi Spasial**: Pemetaan 266 perguruan tinggi eksisting di wilayah Jabodetabek & Karawang dengan klasifikasi multimoda:
  * **Transit-Oriented** (Warna Hijau `#10B981`): Kampus berjarak <= 1.000 meter dari stasiun kereta (KRL/MRT/LRT) atau <= 500 meter dari halte TransJakarta.
  * **Transit-Isolated** (Warna Merah `#EF4444`): Kampus di luar jangkauan radius kedua moda tersebut.
* **Layer Interaktif**: Stasiun Kereta (Biru `#2563EB`), Halte TransJakarta (Ungu `#7C3AED`), dan Zona Buffer Radius 1.000 m.
* **Fitur Tambahan**: Filter status kelembagaan (PTN/PTS), pencarian kampus spesifik, dan Kartu Analisis Dinamis 4-Tier.

### 2. Tab 2: Sistem Rekomendasi Kampus Satelit Berbasis Random Forest ML (Soal 2)
* **Peta Koroplet Rekomendasi**: Pemetaan 299 kecamatan berdasarkan hasil klasifikasi model Machine Learning:
  * **Sangat Direkomendasikan (Kelas 2 — Hijau `#10B981`)**
  * **Cukup Direkomendasikan (Kelas 1 — Kuning `#F59E0B`)**
  * **Tidak Direkomendasikan (Kelas 0 — Merah `#EF4444`)**
* **Atribut Variabel Spasial (Feature Engineering)**:
  1. `sma_grad`: Jumlah lulusan/siswa SMA per kecamatan (36.99% — Paling Menentukan)
  2. `dist_ind`: Jarak ke kawasan industri terdekat (31.10%)
  3. `toll_pct`: Persentase ketersediaan akses jalan tol (17.29%)
  4. `area_km2`: Luas total wilayah kecamatan (10.52%)
  5. `camp_dens`: Kepadatan kampus eksisting per km² (4.09%)
* **Fitur Interaktif**: Filter Kabupaten/Kota & Tingkat Rekomendasi, Grafik Horizontal Feature Importance, dan **Simulator Prediksi ML Real-Time** bagi pengguna untuk menguji inferensi model `RandomForestClassifier.predict()` secara langsung di browser.

---

## Optimalisasi Performa Geometri & Benchmarking Latensi

Untuk mengatasi lag rendering peta poligon kecamatan, diterapkan pipeline penyederhanaan geometri spasial:

* **Skrip Penyederhanaan (`simplify_data.py`)**: Mengolah geometri poligon `Kecamatan_Batas_Kecil.geojson` dengan algoritma Douglas-Peucker (`tolerance=0.0004`) dan pembulatan koordinat 5 desimal, serta melakukan pre-join data atribut prediksi ML.
* **Hasil Efisiensi Ukuran**: Ukuran GeoJSON berkurang dari **17.44 MB menjadi 0.88 MB** (pengurangan **94.98%**).
* **Hasil Benchmarking Latensi (`test_latency.py`)**: Waktu pemuatan data berkurang dari **351.18 ms menjadi 14.16 ms** per render server (**24.8x lebih cepat**).

---

## Struktur Direktori Proyek

```text
.
├── Project/
│   └── UAS.qgz                        # File Workspace QGIS Project Desktop
├── data_ready/
│   ├── Kecamatan_ML_Simplified.geojson # GeoJSON teroptimasi & pre-joined ML (0.88 MB)
│   ├── Kecamatan_Batas_Kecil.geojson  # GeoJSON batas kecamatan versi asal (17.44 MB)
│   ├── Campuses_WebGIS.geojson        # Data spasial perguruan tinggi Jabodetabek
│   ├── Stations_WebGIS.geojson        # Data spasial stasiun KRL/MRT/LRT
│   ├── Halte_TransJakarta.geojson     # Data spasial halte TransJakarta
│   ├── kecamatan_predictions.csv      # Hasil prediksi klasifikasi model ML
│   └── Kecamatan_Jabodetabek.*        # Shapefile kecamatan hasil join spasial
├── docs/
│   ├── Laporan_UAS_GIS_E504.md        # Laporan akademik lengkap (Markdown)
│   ├── Laporan_UAS_GIS_E504.docx      # Laporan akademik resmi (Word Document)
│   ├── Laporan_UAS_GIS_E504.pdf       # Laporan akademik resmi (PDF)
│   └── Soal_UAS_Ruang_E-504.md        # Naskah soal ujian UAS
├── app.py                             # Script utama aplikasi Streamlit WebGIS Multi-Tab
├── simplify_data.py                   # Script penyederhanaan geometri & pre-join ML
├── test_latency.py                    # Script pengujian latensi render spasial
├── test_simplify_data.py              # Unit test untuk penyederhanaan GeoJSON
├── test_app_syntax.py                 # Unit test untuk verifikasi kompilasi app.py
├── calculate_spatial_features_qgis.py # Script Feature Engineering untuk QGIS Console
├── train_qgis.py                      # Script pelatihan Random Forest untuk QGIS Console
├── retrain_standalone.py              # Script pemodelan ulang Machine Learning
├── requirements.txt                   # Dependensi modul Python untuk Streamlit Cloud
└── README.md                          # Dokumentasi umum proyek (file ini)
```

---

## Cara Menjalankan Aplikasi & Pengujian Secara Lokal

```bash
# 1. Jalankan pengujian latensi pemuatan GeoJSON
python3 test_latency.py

# 2. Jalankan unit test validasi geometri & sintaks
python3 test_simplify_data.py
python3 test_app_syntax.py

# 3. Jalankan dashboard WebGIS Streamlit secara lokal
python3 -m streamlit run app.py
```
