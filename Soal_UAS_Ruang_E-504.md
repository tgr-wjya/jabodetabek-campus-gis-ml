# UJIAN AKHIR SEMESTER (UAS)
## SISTEM INFORMASI GEOGRAFIS (W182500032)

| Informasi Akademik | Detail |
| :--- | :--- |
| **No. Dokumen** | 01-1.4.40.00 |
| **Tgl. Efektif** | 1 September 2025 |
| **Nama Dosen** | MOHAMAD YUSUF, S.KOM., MCS |
| **Hari, Tanggal & Jam** | SELASA, 21 JULI 2026, 13.15-15.45 |
| **SKS** | 3 |
| **Tahun Akademik / Semester** | 2025/2026 |
| **Bobot Persentase Asesmen** | 35% |
| **Estimasi Waktu & Tempat** | 180 Menit / Ruang E-504 |
| **Pengerjaan Asesmen** | Individu |

---

### Capaian Pembelajaran Mata Kuliah (CPMK) & Capaian Pembelajaran Lulusan (CPL)

| CPMK | Deskripsi Capaian Pembelajaran Mata Kuliah (CPMK) | Capaian Pembelajaran Lulusan (CPL) |
| :--- | :--- | :--- |
| **CPMK 72.1** | Mampu menyebutkan format umum data spasial (Shapefile, GeoJSON, GeoTIFF, dll). | CPL 7 |
| **CPMK 72.2** | Mampu menjelaskan prinsip Software Development Fundamental (SDF) dalam SIG. | CPL 7 |
| **CPMK 81.1** | Mahasiswa menjelaskan keterkaitan antara OOAD (Object-Oriented Analysis and Design) dengan tahapan SDLC dalam konteks pengembangan sistem informasi modern. | CPL 8 |
| **CPMK 83.1** | Mahasiswa mendesain sistem dengan tahapan SDLC dalam pengembangan sistem informasi modern. | CPL 8 |

---

### PETUNJUK UMUM

1. Mahasiswa wajib hadir tepat waktu sesuai jadwal yang telah ditetapkan.
2. Mahasiswa harus mempersiapkan alat tulis dan perlengkapan yang diperlukan sesuai jenis ujian.
3. Dilarang melakukan plagiarisme atau bekerja sama dengan peserta lain tanpa izin.
4. Kelola waktu dengan baik agar seluruh soal dapat diselesaikan dalam batas waktu yang ditentukan.
5. Penilaian didasarkan sesuai rubrik penilaian UTS/UAS.

---

### VERIFIKASI SOAL UJIAN

| Peran | Nama |
| :--- | :--- |
| **Dosen Pembuat Soal** | MOHAMAD YUSUF, S.KOM., MCS |
| **Ketua Program Studi** | Dr. Hadi Santoso, S.Kom., M.Kom. |

---

## DAFTAR PERTANYAAN UJIAN AKHIR SEMESTER

| Sub-CPMK Mapped | No | Topik / Judul Soal | Bobot |
| :--- | :---: | :--- | :---: |
| CPMK 72.1, CPMK 72.2, 81.1, dan 83.1 | 1 | [Peta Interaktif Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek](#soal-1-peta-interaktif-aksesibilitas-transportasi-massal-perguruan-tinggi-jabodetabek) | 18% |
| CPMK 72.1, CPMK 72.2, 81.1, dan 83.1 | 2 | [Sistem Rekomendasi Lokasi Pembangunan Kampus Satelit/Program Studi Baru Berbasis Machine Learning (Random Forest)](#soal-2-sistem-rekomendasi-lokasi-pembangunan-kampus-satelitprogram-studi-baru-berbasis-machine-learning-random-forest) | 17% |

---

### SOAL 1: Peta Interaktif Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek

#### Latar Belakang
Hasil analisis klasifikasi kampus Transit-Oriented dan Transit-Isolated tidak akan berdampak maksimal jika hanya disimpan dalam format `.shp` atau laporan PDF statis. Dinas Perhubungan, Kemdikbudristek, serta pihak kampus membutuhkan peta yang bisa dibuka langsung di browser (HP/Laptop) tanpa perlu menginstal QGIS, sehingga dapat digunakan untuk perencanaan rute shuttle kampus, integrasi angkutan feeder, maupun sosialisasi akses transportasi kepada calon mahasiswa baru.

#### Tujuan
Mengeksport dan mempublikasikan hasil analisis spasial QGIS menjadi WebGIS sederhana yang interaktif, ringan, dan dapat diakses melalui URL publik.

#### Pilihan Tools (Sangat Sederhana - Pilih Salah Satu)
Mahasiswa **TIDAK DIPERKENANKAN** membuat web dari nol (HTML/CSS/JS murni). Pilih salah satu alat low-code/no-code berikut:
- **Opsi a (No-Code / Pengguna QGIS Murni):** Menggunakan Plugin langsung dari QGIS ke format **QGIS2Web** (Export Leaflet/OpenLayers HTML).
- **Opsi b (Low-Code / Pengguna Python):** Menggunakan **Streamlit + Library Folium atau PyDeck** (Hanya butuh 10-20 baris kode Python).
- **Opsi c (No-Code / Visualisasi Data):** Menggunakan **Kepler.gl atau Mapbox Studio** (Upload data GeoJSON/CSV lalu atur visualisasinya secara drag-and-drop).

#### Tugas dan Langkah Kerja

##### 1. Styling & Simbolisasi (Kartografi Aksesibilitas)
Atur warna layer agar intuitif dan mencerminkan tingkat aksesibilitas:
- **Kampus Transit-Oriented**: Titik berwarna **Hijau** (Akses Baik).
- **Kampus Transit-Isolated**: Titik berwarna **Merah/Oranye** (Akses Buruk/Perlu Intervensi).
- **Stasiun KRL/MRT/LRT**: Titik berwarna **Biru** (Simpul Utama).
- **Halte TransJakarta**: Titik berwarna **Ungu** (Simpul Feeder).
- **Buffer 500m & 1KM**: Poligon Transparan dengan warna berbeda untuk membedakan radius.

##### 2. Pembuatan Interaktivitas Dasar (Pop-up & Layer Control)
- **a. Pop-up Info:** Pastikan setiap fitur yang diklik di peta web memunculkan pop-up berisi atribut penting:
  - **Pada Kampus:** Nama Kampus, Status (PTN/PTS), Akreditasi, Jumlah Mahasiswa, Kategori (Transit-Oriented / Transit-Isolated).
  - **Pada Stasiun/Halte:** Nama Simpul, Jenis Transportasi (KRL/MRT/LRT/TransJakarta).
- **b. Layer Control:** Pengguna bisa menyembunyikan/menampilkan layer melalui checkbox di pojok peta (misal: user bisa mematikan layer "Batas Admin" agar fokus melihat sebaran kampus dan simpul transportasi).
- **c. Filter Dinamis (Opsional tapi Disukai):** Jika menggunakan Streamlit/Kepler.gl, tambahkan dropdown untuk memfilter kampus berdasarkan:
  - Status (PTN saja / PTS saja / Semua)
  - Kategori Aksesibilitas (Transit-Oriented saja / Transit-Isolated saja)

##### 3. Penambahan Konteks
- **a.** Tambahkan **Judul Peta** (misal: *"Peta Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek"*), **Legenda**, dan **Skala** pada layout web.
- **b. Jika menggunakan Streamlit/Kepler.gl:** Tambahkan paragraf teks ringkasan eksekutif di samping peta (misal: *"Ditemukan 25 kampus Transit-Isolated dengan total 85.000 mahasiswa yang bergantung pada angkutan informal untuk mengakses transportasi massal"*).

##### 4. Publikasi (Hosting Gratis)
- **a. Untuk QGIS2Web:** Kompres folder output (yang berisi file `index.html`) dan upload ke GitHub Pages atau Netlify Drop (sistem drag-and-drop, sangat mudah).
- **b. Untuk Streamlit:** Upload kode `app.py` dan data ke Streamlit Community Cloud (gratis).
- **c. Untuk Kepler.gl:** Cukup klik tombol "Share" atau "Export" untuk mendapatkan URL publik.

#### Deliverables (Luaran yang Dikumpulkan)
- **Live URL:** Tautan aktif peta web yang bisa diklik dan dibuka oleh dosen.
- **Screenshot:** 2 buah screenshot tampilan peta (satu tampilan penuh dengan legenda, satu tampilan pop-up kampus yang sedang diklik).
- **Laporan Singkat**

---

### SOAL 2: Sistem Rekomendasi Lokasi Pembangunan Kampus Satelit/Program Studi Baru Berbasis Machine Learning (Random Forest)

#### Latar Belakang
Kementerian Pendidikan dan program Merdeka Belajar mendorong pembukaan Program Studi (Prodi) strategis yang sesuai dengan kebutuhan industri (seperti AI, Energi Terbarukan, Teknik Logistik). Namun, banyak PTS di Jabodetabek yang membuka prodi tanpa kajian spasial yang matang, sehingga terjadi tumpang tindih di pusat kota sementara kawasan industri di Cikarang, Karawang, atau Tangerang Selatan kekurangan pasokan lulusan. Diperlukan model Machine Learning untuk merekomendasikan lokasi optimal pembangunan "Kampus Satelit" atau Prodi baru berdasarkan kedekatan dengan kawasan industri, demografi usia kuliah, dan daya dukung infrastruktur.

#### Tujuan
Mengekstrak fitur spasial (*spatial feature engineering*) dari data geografis Jabodetabek, melatih model Random Forest untuk mengklasifikasikan kecamatan mana yang "Sangat Direkomendasikan", "Direkomendasikan", atau "Tidak Direkomendasikan" untuk pembangunan kampus satelit.

#### Data yang Disediakan
* `Kecamatan_Jabodetabek.shp` (Poligon, 250+ kecamatan, atribut: `Label_Rekomendasi` [2=Sangat, 1=Cukup, 0=Tidak] — sebagai data training).
* `Kawasan_Industri_Jabodetabek.shp` (Poligon - Cikarang, KIIC, MM2100, dll).
* `Jumlah_Lulusan_SMA_Per_Kecamatan.shp` (Poligon, atribut numerik).
* `Akses_Jalan_Tol.shp` (Line).
* `Sebaran_Kampus_Eksisting.shp` (Titik).

#### Tugas dan Langkah Kerja Project

##### Bagian A: Spatial Feature Engineering di QGIS
Data poligon kecamatan harus diperkaya dengan fitur spasial dari layer lain. Jelaskan dan lakukan langkah berikut:
* **a.** Bagaimana cara menghitung variabel `Jarak_ke_Kawasan_Industri_Terdekat` untuk setiap kecamatan? (Tool: *Distance to nearest hub* setelah mengonversi poligon industri ke titik centroid, atau *v.distance*).
* **b.** Bagaimana cara menghitung `Kepadatan_Kampus_Eksisting` (jumlah kampus per KM²) di setiap kecamatan? (Tool: *Count points in polygon* lalu bagi dengan luas area).
* **c.** Bagaimana cara menghitung `Persentase_Akses_Tol` (panjang jalan tol yang memotong kecamatan dibagi luas kecamatan)? (Tool: *Line length in polygon*).
* **d.** Tuliskan 5 variabel independen (fitur) final yang akan masuk ke model!

##### Bagian B: Implementasi Algoritma Random Forest
Gunakan QGIS Python Console dengan library *scikit-learn* atau plugin ML seperti "Scikit Learn Tools" / "Processing R Provider".

Tuliskan pseudo-code Python untuk:
* **a.** Memuat data atribut kecamatan ke dalam `X` (fitur) dan `y` (label Rekomendasi).
* **b.** Membagi data menjadi training set (80%) dan test set (20%).
* **c.** Melatih model `RandomForestClassifier` dan menghitung accuracy score.
* **d.** Jelaskan cara Anda mengekstrak *Feature Importance* dari model dan bagaimana hasil tersebut bisa menjawab pertanyaan: *"Faktor apa yang paling menentukan rekomendasi lokasi kampus satelit — kedekatan dengan industri, atau jumlah lulusan SMA?"*

##### Bagian C: Pemetaan Hasil & Kesimpulan
Setelah model memprediksi label untuk kecamatan yang belum memiliki label (atau memvalidasi label eksisting), bagaimana cara Anda memvisualisasikan hasil prediksi ke dalam Peta QGIS? (Jelaskan proses Join tabel hasil prediksi ke layer `Kecamatan_Jabodetabek.shp` dan pengaturan *Graduated Symbology* dengan skema warna: **Hijau** = Sangat Direkomendasikan, **Kuning** = Cukup, **Merah** = Tidak).
