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

### 4. Hasil Analisis Spasial
Dari total **274 kampus** yang dipetakan di wilayah Jabodetabek dan Karawang:
*   **Transit-Oriented**: **112 Kampus (40.9%)**. Kampus-kampus ini memiliki integrasi multimoda yang baik, memudahkan mahasiswa menggunakan transportasi umum massal.
*   **Transit-Isolated**: **162 Kampus (59.1%)**.
*   **Estimasi Mahasiswa Terdampak**: Teridentifikasi sekitar **1.570.303 mahasiswa** berkuliah di kampus *Transit-Isolated*, di mana sebagian besar terpusat di kawasan penyangga (Bekasi, Tangerang, Depok, dan Karawang) yang belum terlayani jaringan transportasi massal secara memadai.

### 5. Implementasi WebGIS Dashboard (Streamlit + Folium)
Platform dikembangkan menggunakan **Streamlit** (Python web framework) dan pustaka kartografi **Folium (Leaflet.js)**. Kode aplikasi dapat dilihat pada berkas `app.py`.

#### Fitur Utama Dashboard:
1.  **Filter Interaktif**: Pengguna dapat menyaring sebaran kampus berdasarkan Status (Semua, PTN saja, PTS saja) dan Kategori Aksesibilitas.
2.  **Layer Control Toggles**: Mengontrol tampilan visual layer Batas Kecamatan, Stasiun, Halte TransJakarta, dan visualisasi radius buffer stasiun.
3.  **Informasi Pop-up Detil**: Mengklik titik kampus akan menampilkan tabel properti berisi Nama Kampus, Status PTN/PTS, Akreditasi, Jumlah Mahasiswa, Kategori Akses, serta jarak presisi dalam meter ke stasiun dan halte TransJakarta terdekat.
4.  **Skema Warna Kartografi**:
    *   *Kampus Transit-Oriented*: Titik Hijau.
    *   *Kampus Transit-Isolated*: Titik Merah.
    *   *Stasiun*: Titik Biru.
    *   *Halte TransJakarta*: Titik Ungu.
5.  **Hosting Publik**: Tautan aktif WebGIS: [https://uas-gis-e504.streamlit.app/](https://uas-gis-e504.streamlit.app/)
6.  **Repositori GitHub**: Seluruh berkas kode sumber WebGIS, data Shapefile, dan script pemrosesan di-host secara privat di: [https://github.com/tgr-wjya/uas-gis-e504](https://github.com/tgr-wjya/uas-gis-e504)

#### Screenshot Tampilan Peta Interaktif (WebGIS):
*   **Visual 1: Tampilan Penuh WebGIS & Legenda**
    ![Screenshot 1: Tampilan Penuh WebGIS & Legenda](/home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/screenshot/screenshot1.png)
    *Gambar 1.1: Tampilan Peta Interaktif WebGIS Aksesibilitas Perguruan Tinggi Jabodetabek*

*   **Visual 2: Tampilan Pop-up Atribut Kampus**
    ![Screenshot 2: Tampilan Pop-up Atribut Kampus](/home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/screenshot/screenshot2.png)
    *Gambar 1.2: Tampilan Pop-up Atribut Detail Kampus (Kalbis Institute)*

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
    5.  `area_km2`: Luas total wilayah kecamatan (km²).

#### Bukti Eksekusi Prosedur Feature Engineering di QGIS Console:
![Bukti Eksekusi Prosedur Feature Engineering di QGIS Console](/home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/screenshot/Screenshot from 2026-07-19 18-51-45.png)
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
![Bukti Eksekusi QGIS Python Console](/home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/screenshot/Screenshot from 2026-07-19 17-54-38.png)
*Gambar 2.2: Bukti Eksekusi Pemodelan Spasial Random Forest pada QGIS Python Console*

---

### Bagian C: Pemetaan Hasil & Kesimpulan

#### 1. Proses Visualisasi Hasil Prediksi (Join Tabel ke Layer Spasial)
Untuk menampilkan hasil klasifikasi rekomendasi dari model Random Forest ke dalam peta QGIS:
1.  **Ekspor Prediksi**: Hasil prediksi model dijalankan untuk seluruh 299 kecamatan dan disimpan ke berkas [kecamatan_predictions.csv](file:///home/tgrwjya/Documents/Uni/Semester%206/DATA/GIS/UAS/data_ready/kecamatan_predictions.csv).
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
![Peta Cetak Layout QGIS](/home/tgrwjya/Documents/Uni/Semester 6/DATA/GIS/UAS/screenshot/Peta Rekomendasi Lokasi Kampus Satelit Baru Berbasis Machine Learning Print Layout.png)
*Gambar 2.3: Peta Hasil Klasifikasi Kelayakan Lokasi Kampus Satelit Baru (Output QGIS Print Layout)*
