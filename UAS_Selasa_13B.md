# UJIAN AKHIR SEMESTER (UAS)
## SISTEM INFORMASI GEOGRAFIS (W182500032)

![Universitas Mercu Buana – Kompaspedia](data:image/png;base64...)

| Informasi Akademik | Detail |
| :--- | :--- |
| **Nama Dosen** | MOHAMAD YUSUF, S.KOM., MCS |
| **Hari, Tanggal & Jam** | SELASA, 21 JULI 2026, 13.15-15.45 |
| **SKS** | 3 |
| **Tahun Akademik / Semester** | 2025/2026 |
| **Bobot Persentase Asesmen** | 35% |
| **Estimasi Waktu & Tempat** | 180 Menit / Online |
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

| Peran | Nama | Status |
| :--- | :--- | :--- |
| **Dosen Pembuat Soal** | MOHAMAD YUSUF, S.KOM., MCS | Terverifikasi |
| **Ketua Program Studi** | Dr. Hadi Santoso, S.Kom., M.Kom. | Terverifikasi (Tanda Tangan) |

---

## DAFTAR PERTANYAAN UJIAN AKHIR SEMESTER

| Sub-CPMK Mapped | No | Topik / Judul Soal | Bobot |
| :--- | :---: | :--- | :---: |
| CPMK 72.1, CPMK 72.2, 81.1, dan 83.1 | 1 | [Peta Interaktif Monitoring Kapasitas Taman Makam Umum (TMU) dan Aksesibilitas RPTRA di DKI Jakarta](#soal-1-peta-interaktif-monitoring-kapasitas-taman-makam-umum-tmu-dan-aksesibilitas-rptra-di-dki-jakarta) | 18% |
| CPMK 72.1, CPMK 72.2, 81.1, dan 83.1 | 2 | [Sistem Pendukung Keputusan Lokasi Optimal Pembangunan RPTRA Baru dengan Mempertimbangkan Zona Eksklusi TMU Berbasis Machine Learning (Random Forest)](#soal-2-sistem-pendukung-keputusan-lokasi-optimal-pembangunan-rptra-baru-dengan-mempertimbangkan-zona-eksklusi-tmu-berbasis-machine-learning-random-forest) | 17% |

---

### SOAL 1: Peta Interaktif Monitoring Kapasitas Taman Makam Umum (TMU) dan Aksesibilitas RPTRA di DKI Jakarta

#### Latar Belakang
Dinas Pertamanan dan Hutan Kota serta Dinas Pemberdayaan Perempuan dan Perlindungan Anak (PPPA) membutuhkan pemantauan spasial secara *real-time*. Banyak TMU di Jakarta yang sudah hampir penuh (*overcapacity*) dan memerlukan perluasan atau relokasi, sementara di sisi lain, sebaran RPTRA (Ruang Publik Terpadu Ramah Anak) harus dipastikan menjangkau area padat penduduk anak-anak tanpa berada di zona yang tidak sehat (misal: terlalu dekat dengan TMU yang memiliki isu lingkungan/psikologis). Hasil analisis spasial ini harus dipublikasikan ke dalam WebGIS agar dapat diakses oleh Walikota, Camat, dan publik tanpa perlu software desktop.

#### Tujuan
Mengeksport dan mempublikasikan hasil analisis spasial QGIS menjadi WebGIS sederhana yang interaktif untuk monitoring kapasitas TMU dan sebaran RPTRA.

#### Pilihan Tools (Sangat Sederhana - Pilih Salah Satu)
Mahasiswa **TIDAK DIPERKENANKAN** membuat web dari nol. Pilih salah satu alat low-code/no-code berikut:
- **Opsi 1 (No-Code):** Plugin QGIS2Web (Export ke Leaflet/OpenLayers).
- **Opsi 2 (Low-Code):** Streamlit + Folium/PyDeck (Python).
- **Opsi 3 (No-Code):** Kepler.gl atau Mapbox Studio (Drag-and-drop).

#### Tugas dan Langkah Kerja

##### 1. Styling & Simbolisasi (Kartografi Monitoring)
- **a.** Atur warna layer agar intuitif.
- **b.** TMU: Poligon/Titik **Hijau** (Kapasitas > 30%), **Kuning** (10-30%), **Merah** (Kritis / < 10%).
- **c.** RPTRA: Titik **Biru** (Fasilitas Lengkap), **Ungu** (Fasilitas Terbatas).
- **d.** Buffer Eksklusi TMU: Poligon Transparan Radius 500m (Zona penyangga agar RPTRA tidak dibangun terlalu dekat dengan TMU).

##### 2. Pembuatan Interaktivitas Dasar (Pop-up & Layer Control)
- **a.** **Pop-up Info:** Pastikan setiap fitur yang diklik di peta web memunculkan pop-up berisi atribut penting:
  - **Pada TMU:** Nama TMU, Luas Area, Status Kapasitas (Tersedia/Kritis), Tahun Berdiri.
  - **Pada RPTRA:** Nama RPTRA, Fasilitas Utama (Perpustakaan/Biopori/Playground), Kondisi.
- **b.** **Layer Control:** Checkbox untuk menyembunyikan/menampilkan layer (misal: mematikan layer "Batas Kelurahan" agar fokus pada sebaran TMU dan RPTRA).
- **c.** **Filter Dinamis (Opsional tapi Disukai):** Dropdown untuk memfilter berdasarkan Wilayah Administrasi (Jakarta Pusat, Selatan, dll) atau Status Kapasitas TMU.

##### 3. Penambahan Konteks
- **a.** Tambahkan Judul Peta, Legenda, dan Skala.
- **b.** Tambahkan 1 paragraf teks ringkasan eksekutif (misal: *"Ditemukan 4 TMU di Jaksel berstatus kritis dengan kapasitas di bawah 10%, sementara 15 RPTRA di Jakut belum terlayani dalam radius jalan kaki 1 KM"*).

##### 4. Publikasi (Hosting Gratis)
- **a.** Upload ke GitHub Pages, atau gunakan fitur Share URL dari Kepler.gl.

#### Deliverables (Luaran yang Dikumpulkan)
- **a. Live URL:** Tautan aktif peta web.
- **b. Screenshot:** 2 buah (tampilan penuh dengan legenda, dan tampilan pop-up TMU/RPTRA yang diklik).
- **c. Laporan**

---

### SOAL 2: Sistem Pendukung Keputusan Lokasi Optimal Pembangunan RPTRA Baru dengan Mempertimbangkan Zona Eksklusi TMU Berbasis Machine Learning (Random Forest)

#### Latar Belakang
Pembangunan RPTRA baru seringkali terkendala lahan kosong yang terbatas dan konflik tata ruang. Selain itu, secara psikologis dan lingkungan, RPTRA (yang ditujukan untuk anak-anak) idealnya tidak dibangun berdekatan dengan Taman Makam Umum (TMU). Diperlukan model Machine Learning untuk memprediksi dan merekomendasikan RW mana yang "Sangat Prioritas" untuk dibangun RPTRA baru, dengan syarat: memiliki lahan kosong, jauh dari buffer TMU, dan memiliki kepadatan anak yang tinggi.

#### Tujuan
Melatih model Random Forest untuk mengklasifikasikan kelayakan lokasi pembangunan RPTRA baru berdasarkan *spatial feature engineering*.

#### Data yang Disediakan
1. `Batas_RW_Jakarta.shp` (Poligon, atribut: `Label_Prioritas` [2=Sangat, 1=Cukup, 0=Tidak] — sebagai data training).
2. `Lokasi_TMU.shp` (Poligon/Titik).
3. `Kepadatan_Penduduk_Anak.shp` (Poligon/Raster).
4. `Lahan_Kosong_Pemkot.shp` (Poligon).
5. `Jaringan_Jalan.shp` (Line).

#### Tugas dan Langkah Kerja Project

##### Bagian A: Spatial Feature Engineering di QGIS
Data poligon RW harus diperkaya dengan fitur spasial. Jelaskan dan lakukan langkah berikut:
- **a.** Bagaimana cara menghitung variabel `Jarak_Minimal_ke_TMU` untuk setiap RW? (Tool: *Distance to nearest hub* atau *v.distance* untuk memastikan RPTRA aman dari dampak lingkungan/psikologis TMU).
- **b.** Bagaimana cara menghitung `Persentase_Lahan_Kosong` di setiap RW? (Tool: *Intersection* antara RW dan Lahan Kosong, lalu dibagi luas total RW).

##### Bagian B: Implementasi Algoritma Random Forest
Gunakan QGIS Python Console dengan library *scikit-learn* atau plugin ML.

Tuliskan pseudo-code Python untuk:
- **a.** Memuat data atribut RW ke dalam `X` (fitur) dan `y` (label Prioritas).
- **b.** Membagi data menjadi training set (80%) dan test set (20%).
- **c.** Melatih model `RandomForestClassifier` dan menghitung accuracy score.

##### Bagian C: Pemetaan Hasil & Kesimpulan
- **a.** Setelah model memprediksi label untuk RW yang belum memiliki label, bagaimana cara Anda memvisualisasikan hasil prediksi ke dalam Peta QGIS? (Jelaskan proses Join tabel hasil prediksi ke layer `Batas_RW` dan pengaturan *Graduated Symbology*: **Hijau** = Sangat Prioritas, **Kuning** = Cukup, **Merah** = Tidak).
- **b.** **Essay Kesimpulan:** Berdasarkan konsep *Spatial Decision Support System* (SDSS), bandingkan pendekatan konvensional (pembangunan RPTRA berdasarkan usulan politik warga/RT) dengan pendekatan ML-Spasial yang Anda bangun. Bagaimana model ini dapat menjamin hak anak atas ruang terbuka hijau yang aman dan sehat? Sebutkan 1 risiko/limitasi model ini (misal: status kepemilikan lahan kosong yang bermasalah secara hukum) yang perlu diwaspadai oleh pembuat kebijakan!