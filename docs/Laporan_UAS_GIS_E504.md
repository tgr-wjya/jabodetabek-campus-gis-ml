# LAPORAN UJIAN AKHIR SEMESTER (UAS)
## SISTEM INFORMASI GEOGRAFIS (W182500032)

| Informasi Mahasiswa | Detail |
| :--- | :--- |
| **Nama Lengkap** | TEGAR WIJAYA KUSUMA |
| **Nomor Induk Mahasiswa (NIM)** | 41523010217 |
| **Program Studi / Fakultas** | Teknik Informatika / Ilmu Komputer |
| **Kelas / Ruang** | E-504 |
| **Hari, Tanggal & Waktu** | SELASA, 21 JULI 2026, 13.15-15.45 |
| **Nama Dosen** | MOHAMAD YUSUF, S.KOM., MCS |

---

## SOAL 1: Peta Interaktif Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek

### 1. Latar Belakang dan Tujuan
Hasil analisis spasial terkait klasifikasi kampus yang memiliki aksesibilitas baik (*Transit-Oriented*) dan yang terisolasi dari akses transportasi umum (*Transit-Isolated*) tidak akan optimal jika hanya disajikan dalam bentuk berkas Shapefile (`.shp`) atau laporan statis. 

Pihak pembuat kebijakan seperti Dinas Perhubungan, Kemdikbudristek, dan pengelola universitas membutuhkan platform peta interaktif yang dapat diakses dengan mudah melalui peramban web (browser HP/Laptop) tanpa perlu menginstal perangkat lunak QGIS. Tujuannya adalah untuk memudahkan perencanaan rute angkutan pengumpan (*shuttle* kampus), integrasi angkutan *feeder* (seperti TransJakarta), serta sosialisasi aksesibilitas bagi calon mahasiswa baru.

### 2. Metodologi dan Sourcing Data Spasial
Untuk menyusun peta interaktif yang akurat dan kredibel, dilakukan pengumpulan data dari berbagai sumber resmi dan komunitas spasial:
1.  **Lokasi Kampus (Perguruan Tinggi)**: Diperoleh dari data OpenStreetMap (OSM) via Overpass Turbo dengan query `amenity=university` dan `amenity=college` di wilayah Jabodetabek dan Karawang, kemudian divalidasi dan diperkaya dengan metadata status (PTN/PTS), akreditasi institusi, dan jumlah mahasiswa aktif berdasarkan pangkalan data **PDDikti**.
2.  **Simpul Utama (Stasiun Transportasi Massal)**: Mengunduh lokasi stasiun KRL Commuter Line, MRT Jakarta, dan LRT (Jakarta & Jabodebek) di wilayah cakupan menggunakan query `railway=station` dari OpenStreetMap.
3.  **Simpul Pengumpan (Halte TransJakarta)**: Mengunduh koordinat halte bus TransJakarta menggunakan query OSM untuk `highway=bus_stop` dengan operator TransJakarta.
4.  **Batas Administrasi Kecamatan**: Batas kecamatan di wilayah Jabodetabek dan Karawang disederhanakan dari batas resmi BIG/BPS untuk memastikan efisiensi memori render WebGIS.

### 3. Aturan Klasifikasi Aksesibilitas Spasial
Klasifikasi aksesibilitas perguruan tinggi dianalisis secara spasial dalam sistem koordinat proyeksi **UTM Zone 48S (EPSG:32748)** untuk menghitung jarak dalam satuan meter yang akurat:
*   **Transit-Oriented** (Akses Baik): Kampus terletak dalam radius **<= 1.000 meter** dari stasiun kereta (KRL/MRT/LRT) ATAU dalam radius **<= 500 meter** dari halte bus TransJakarta.
*   **Transit-Isolated** (Akses Buruk): Kampus terletak di luar kedua radius tersebut.

### 4. Hasil Analisis Spasial & Sanitasi Data (Data Pruning)
Dari hasil pembersihan, penggabungan, dan validasi data spasial (*data pruning & disambiguation*), dataset disanitasi dari 274 entri awal menjadi **266 perguruan tinggi tervalidasi**:
1.  **Sanitasi & Pembersihan Duplikasi**: Menghapus 8 entri duplikat/invalid (seperti node duplikat IPB Baranangsiang, Ibnu Chaldun, UPJ, Universitas Raharja, dan UPH Lippo Village), memulihkan entri generik *"Perguruan Tinggi"* menjadi entitas resmi (seperti USNI, UNTAR, Ibn Khaldun Bogor, dll.), serta melakukan *disambiguation* nama kampus multi-lokasi (seperti *Universitas Mercu Buana – Kampus Meruya / Menteng / Warung Buncit*, *UNJ Kampus A/B/C/D*, *Esa Unggul*, *UI Depok/Salemba*, dll.).
2.  **Normalisasi Akreditasi**: Mengonversi 63 entri skala akreditasi lama (A/B/C) menjadi standar nasional terbaru BAN-PT (*Unggul / Baik Sekali / Baik*).
3.  **Klasifikasi Keseluruhan**:
    *   **Transit-Oriented**: **128 Kampus (48.1%)** dengan total **1.170.840 mahasiswa**.
    *   **Transit-Isolated**: **138 Kampus (51.9%)** dengan total **1.126.456 mahasiswa**.
4.  **Analisis Segmentasi Kelembagaan (PTN vs PTS)**:
    *   **Perguruan Tinggi Negeri (PTN — 41 Kampus / 513.346 Mahasiswa)**: Sebanyak **19 kampus PTN (46.3%)** berstatus *Transit-Oriented* dan **22 kampus PTN (53.7%)** berstatus *Transit-Isolated*. Kampus utama PTN (seperti *UI Depok* dengan jarak stasiun 630 m dan *UNJ Kampus A Rawamangun*) terintegrasi langsung dengan koridor utama rel KRL dan halte TransJakarta. Namun, kampus vokasi/satelit di kawasan luar (seperti *IPB Dramaga* atau *UPN Veteran Limo*) terisolasi dari jaringan transportasi rel, berdampak pada **221.840 mahasiswa PTN**.
    *   **Perguruan Tinggi Swasta (PTS — 225 Kampus / 1.783.950 Mahasiswa)**: Sektor swasta mendominasi lanskap pendidikan tinggi di wilayah Jabodetabek & Karawang dengan menampung **77.7% total mahasiswa**. Sebanyak **116 kampus PTS (51.6%)** tergolong *Transit-Isolated*, berdampak langsung pada **904.616 mahasiswa**. Hal ini didorong oleh pola ekspansi kampus swasta di wilayah penyangga (Tangerang, Bekasi, Karawang, Depok) sepanjang jalan arteri yang jauh dari jaringan rel, memicu ketergantungan tinggi pada kendaraan pribadi.

### 5. Implementasi WebGIS Dashboard (Streamlit + Folium)
Platform dikembangkan menggunakan **Streamlit** (Python web framework) dan pustaka kartografi **Folium (Leaflet.js)**. Kode aplikasi dapat dilihat pada berkas `app.py`.

#### Fitur Utama & Mesin Analisis Dapur Dashboard:
1.  **Filter Interaktif Multi-Kriteria**: Pengguna dapat menyaring sebaran kampus berdasarkan Status (Semua, PTN saja, PTS saja) dan Kategori Aksesibilitas (Transit-Oriented, Transit-Isolated).
2.  **Mesin Kartu Analisis Dinamis 4-Tier (*4-Tier Dynamic Analysis Engine*)**:
    *   *Tier 1 (Pencarian Kampus Spesifik)*: Saat pengguna memilih kampus tertentu (misal: *Universitas Mercu Buana – Kampus Meruya* vs *Menteng*), sistem menghasilkan diagnosa spasial mikro berisi status PTN/PTS, akreditasi, populasi mahasiswa, jarak presisi ke stasiun & halte TransJakarta, serta rekomendasi kebijakan feeder lokal.
    *   *Tier 2 (Filter Kelembagaan PTN/PTS)*: Menyajikan sintesis statistik segmentasi kelembagaan dan dampak beban mobilitas mahasiswa per kelompok.
    *   *Tier 3 (Filter Kategori Akses)*: Menyajikan evaluasi kelompok Transit-Oriented vs Transit-Isolated.
    *   *Tier 4 (Tampilan Netral Default)*: Menyajikan ringkasan netral lanskap 266 kampus tanpa prasangka kategori tertentu.
3.  **Layer Control Toggles & High-Contrast Boundary**: Mengontrol tampilan visual layer Batas Kecamatan (reprojected EPSG:4326 dengan efek hover glow `#1D4ED8`), Stasiun Kereta, Halte TransJakarta, dan visualisasi radius buffer stasiun.
4.  **Informasi Pop-up Detil**: Mengklik titik kampus akan menampilkan tabel properti berisi Nama Kampus, Status PTN/PTS, Akreditasi, Jumlah Mahasiswa, Kategori Akses, serta jarak presisi dalam meter.
5.  **Hosting Publik**: Tautan aktif WebGIS: [https://uas-gis-e504.streamlit.app/](https://uas-gis-e504.streamlit.app/)
6.  **Repositori GitHub**: Seluruh berkas kode sumber WebGIS, data Shapefile, dan script pemrosesan di-host secara privat di: [https://github.com/tgr-wjya/uas-gis-e504](https://github.com/tgr-wjya/uas-gis-e504)

#### Screenshot & Diagnosa Tampilan Peta Interaktif (WebGIS):

*   **Visual 1: Tampilan Utama Netral WebGIS Dashboard**
    ![Visual 1: Tampilan Utama Netral WebGIS Dashboard](screenshot/web/Default.png)
    *Gambar 1.1: Tampilan Netral Default WebGIS Menyajikan Overview 266 Perguruan Tinggi Jabodetabek & Karawang*

*   **Visual 2: Filter Segmentasi Perguruan Tinggi Negeri (PTN Only)**
    ![Visual 2: Filter Segmentasi Perguruan Tinggi Negeri (PTN Only)](screenshot/web/PTN_Only.png)
    *Gambar 1.2: Hasil Query Segmentasi PTN Menunjukkan 19 Kampus Transit-Oriented vs 22 Kampus Transit-Isolated*

*   **Visual 3: Filter Segmentasi Perguruan Tinggi Swasta (PTS Only)**
    ![Visual 3: Filter Segmentasi Perguruan Tinggi Swasta (PTS Only)](screenshot/web/PTS_Only.png)
    *Gambar 1.3: Hasil Query Segmentasi PTS Menunjukkan Dominasi 116 Kampus Transit-Isolated (904.616 Mahasiswa Terdampak)*

*   **Visual 4: Filter Sebaran Kampus Transit-Isolated**
    ![Visual 4: Filter Sebaran Kampus Transit-Isolated](screenshot/web/Transit-Isolated_Only.png)
    *Gambar 1.4: Pemetaan 138 Kampus Transit-Isolated yang Membutuhkan Intervensi Angkutan Feeder Regional*

*   **Visual 5: Diagnosa Spasial Kampus Universitas Mercu Buana – Kampus Meruya (A)**
    ![Visual 5: Diagnosa Spasial Kampus Universitas Mercu Buana Meruya](screenshot/web/Mercu-Buana-Meruya_Only.png)
    *Gambar 1.5: Diagnosa Spasial Kampus Meruya (Transit-Isolated, Jarak Stasiun 5.475 m, Halte TJ 610 m, 25.000 Mahasiswa)*

*   **Visual 6: Diagnosa Spasial Kampus Universitas Mercu Buana – Kampus Menteng (B)**
    ![Visual 6: Diagnosa Spasial Kampus Universitas Mercu Buana Menteng](screenshot/web/Mercu-Buana-Menteng_Only.png)
    *Gambar 1.6: Diagnosa Spasial Kampus Menteng (Transit-Oriented, Terintegrasi Koridor Transit Jakarta Pusat)*

*   **Visual 7: Peta Hasil Cetak (QGIS Print Layout)**
    ![Visual 7: Peta Hasil Cetak (QGIS Print Layout)](screenshot/Peta Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek.png)
    *Gambar 1.7: Peta Hasil Cetak Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek (QGIS Layout)*

---

## SOAL 2: Sistem Rekomendasi Lokasi Pembangunan Kampus Satelit Berbasis Machine Learning (Random Forest)

### Bagian A: Spatial Feature Engineering di QGIS

Sebelum melatih model Random Forest, data atribut poligon kecamatan diperkaya dengan variabel spasial menggunakan perangkat analisis QGIS:

1.  **Jarak ke Kawasan Industri Terdekat (`dist_ind`)**:
    *   *Langkah Kerja*: Poligon kawasan industri (`Kawasan_Industri_Jabodetabek.shp`) dikonversi menjadi titik centroid menggunakan tool **Centroids** (di bawah *Vector Geometry*). Jarak antara centroid kecamatan ke centroid industri terdekat dihitung menggunakan tool **Distance to nearest hub (points)** dari toolbox QGIS Processing, menghasilkan kolom jarak dalam satuan meter.
2.  **Kepadatan Kampus Eksisting (`camp_dens`)**:
    *   *Langkah Kerja*: Jumlah kampus eksisting di setiap kecamatan dihitung menggunakan tool **Count points in polygon** dengan layer input poligon kecamatan dan layer input titik kampus (`Sebaran_Kampus_Eksisting.shp`). Kolom jumlah titik yang dihasilkan kemudian dibagi dengan luas area kecamatan (diambil dari `$area / 1000000` menggunakan Field Calculator untuk mendapatkan luas dalam km²), menghasilkan kepadatan per km².
3.  **Persentase Akses Tol (`toll_pct`)**:
    *   *Langkah Kerja*: Jaringan jalan tol (`Akses_Jalan_Tol.shp`) dipotong berdasarkan batas kecamatan menggunakan tool **Intersection**. Panjang segmen tol hasil pemotongan dihitung menggunakan fungsi `$length` di Field Calculator. Persentase akses tol dihitung dengan membagi panjang total jalan tol di dalam kecamatan dengan luas area kecamatan (satuan meter/meter persegi).
4.  **5 Variabel Independen (Fitur) Final**:
    1.  `dist_ind`: Jarak ke kawasan industri terdekat (meter).
    2.  `camp_dens`: Kepadatan kampus eksisting (jumlah/km²).
    3.  `toll_pct`: Rasio panjang jalan tol terhadap luas kecamatan (m/m²).
    4.  `sma_grad`: Jumlah lulusan/siswa SMA (proxy angka sekolah).
5.  **Perbaikan Transformasi Sistem Koordinat (CRS Reprojection Fix)**:
    *   *Permasalahan*: Sebelumnya, variabel `camp_dens` dan `toll_pct` bernilai 0% karena adanya *CRS mismatch* antara layer poligon kecamatan (UTM Zone 48S - EPSG:32748) dengan layer overlay WGS84 (EPSG:4326).
    *   *Solusi*: Menambahkan fungsi `QgsCoordinateTransform` (atau `pyproj.Transformer`) pada script pemrosesan untuk mentransformasi seluruh geometri overlay (titik kampus, garis tol, dan centroid industri) ke dalam sistem koordinat proyeksi kecamatan (EPSG:32748) sebelum melakukan analisis spasial (`contains`, `intersects`, `distance`). Hal ini mengembalikan fungsi fitur `camp_dens` (4.09%) dan `toll_pct` (17.29%) sehingga berkontribusi aktif dalam klasifikasi model.

#### Bukti Eksekusi Prosedur Feature Engineering di QGIS Console:
![Bukti Eksekusi Prosedur Feature Engineering di QGIS Console](screenshot/QGIS/Screenshot from 2026-07-19 17-55-34.png)
*Gambar 2.1: Bukti Eksekusi Script Pemrosesan Variabel Spasial di QGIS Python Console*

---

### Bagian B: Implementasi Algoritma Random Forest

Pemodelan klasifikasi kelayakan lokasi kampus satelit baru dilatih menggunakan library `scikit-learn` pada lingkungan Python.

#### 1. Kode Python untuk Pemodelan (QGIS Python Console):
```python
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Memuat layer aktif Kecamatan_Jabodetabek
layer = iface.activeLayer()

if not layer or layer.name() not in ["Kecamatan_Jabodetabek", "Kecamatan_Jabodetabek_Karawang"]:
    print("Silakan pilih layer 'Kecamatan_Jabodetabek' terlebih dahulu!")
else:
    feature_names = ["dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2"]
    X_rows = []
    y_rows = []
    metadata = []
    
    for feature in layer.getFeatures():
        metadata.append({
            "KODE_KEC": feature["KODE_KEC"],
            "KECAMATAN": feature["KECAMATAN"],
            "KAB_KOTA": feature["KAB_KOTA"]
        })
        X_rows.append([
            float(feature["dist_ind"]),
            float(feature["camp_dens"]),
            float(feature["toll_pct"]),
            float(feature["sma_grad"]),
            float(feature["area_km2"])
        ])
        y_rows.append(int(feature["Label_Reko"]))
        
    X = np.array(X_rows)
    y = np.array(y_rows)
    
    # Membagi data training (80%) dan testing (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Melatih RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
    model.fit(X_train, y_train)
    
    # Evaluasi akurasi
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("="*40)
    print(f"Model Accuracy Score: {accuracy:.4f}")
    print("="*40)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature Importance
    print("\nFeature Importance:")
    for name, imp in zip(feature_names, model.feature_importances_):
        print(f"  {name:<10} : {imp:.4f} ({imp*100:.1f}%)")
```

#### 2. Metrik Evaluasi Model:
*   **Accuracy Score**: **`0.8500` (85.00%)**
*   **Classification Report**:
    *   *Precision & Recall (Kelas 2 - Sangat Direkomendasikan)*: Precision sebesar **0.82** dan Recall mencapai **1.00** (F1-Score = 0.90). Model sangat andal dalam mengidentifikasi wilayah potensial tinggi tanpa ada yang terlewat.
    *   *Precision & Recall (Kelas 0 - Tidak Direkomendasikan)*: Precision **0.84**, Recall **0.89** (F1-Score = 0.86).

#### 3. Analisis Feature Importance:
*   `sma_grad` (Jumlah Lulusan SMA): **36.99%**
*   `dist_ind` (Jarak ke Kawasan Industri): **31.10%**
*   `toll_pct` (Akses Jalan Tol): **17.29%**
*   `area_km2` (Luas Kecamatan): **10.52%**
*   `camp_dens` (Kepadatan Kampus Eksisting): **4.09%**

*   **Faktor Paling Menentukan**: Faktor yang paling menentukan klasifikasi kelayakan lokasi kampus satelit adalah **Jumlah Lulusan/Siswa SMA (`sma_grad`)** dengan tingkat pengaruh **36.99%**, diikuti oleh **Jarak ke Kawasan Industri (`dist_ind`)** sebesar **31.10%**. 
    
    Hal ini menjawab hipotesis awal bahwa keberadaan pasokan calon mahasiswa (input demografis) di suatu kecamatan dinilai lebih kritis oleh model dibandingkan hanya kedekatan dengan kawasan industri mitra, meskipun keduanya merupakan komponen dominan (total kontribusi > 68%).

#### Bukti Eksekusi QGIS Python Console:
![Bukti Eksekusi QGIS Python Console](screenshot/QGIS/Screenshot from 2026-07-19 17-52-26.png)
*Gambar 2.2: Bukti Eksekusi Pemodelan Spasial Random Forest pada QGIS Python Console*

---

### Bagian C: Pemetaan Hasil & Kesimpulan

#### 1. Proses Visualisasi Hasil Prediksi (Join Tabel ke Layer Spasial)
Untuk menampilkan hasil klasifikasi rekomendasi dari model Random Forest ke dalam peta QGIS:
1.  **Ekspor Prediksi**: Hasil prediksi model dijalankan untuk seluruh 299 kecamatan dan disimpan ke berkas [kecamatan_predictions.csv](file:///home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/data_ready/kecamatan_predictions.csv).
2.  **Impor ke QGIS**: Berkas CSV dimuat ke QGIS melalui menu *Layer -> Add Layer -> Add Delimited Text Layer...* dengan pengaturan *No geometry* (hanya berupa tabel atribut).
3.  **Proses Join**:
    *   Buka menu **Properties** pada layer spasial utama **`Kecamatan_Jabodetabek`**.
    *   Pilih tab **Joins** dan klik ikon **+** (tambah join baru).
    *   Tentukan *Join layer* sebagai `kecamatan_predictions`, *Join field* sebagai `KODE_KEC`, dan *Target field* pada shapefile sebagai `KODE_KEC`. Klik *OK*. Prosedur ini menggabungkan kolom hasil prediksi (`Pred_Reko`) ke tabel atribut spasial secara dinamis.
4.  **Pengaturan Symbology**:
    *   Pada jendela Properties layer `Kecamatan_Jabodetabek`, buka tab **Symbology**.
    *   Ubah tipe render dari *Single Symbol* menjadi **Graduated**.
    *   Pilih kolom **`Pred_Reko`** sebagai kolom nilai (*Value*).
    *   Gunakan metode klasifikasi **Equal Interval** dengan **3 kelas**.
    *   Sesuaikan warna simbol untuk masing-masing nilai kelas secara manual:
        *   Nilai `2` (Sangat Direkomendasikan): **Hijau** (menandakan kesesuaian tinggi dengan industri, tol, dan ketersediaan siswa).
        *   Nilai `1` (Cukup Direkomendasikan): **Kuning**.
        *   Nilai `0` (Tidak Direkomendasikan): **Merah** (wilayah dengan kepadatan kampus tinggi/jenuh atau jauh dari industri/akses tol).
    *   Klik *Apply* lalu *OK*. Peta QGIS kini menampilkan zonasi kelayakan lokasi pembangunan kampus satelit secara intuitif.

#### Peta Hasil Cetak (QGIS Print Layout):
![Peta Cetak Layout QGIS](screenshot/Peta Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek.png)
*Gambar 2.3: Peta Hasil Klasifikasi Kelayakan Lokasi Kampus Satelit Baru (Output QGIS Print Layout)*
