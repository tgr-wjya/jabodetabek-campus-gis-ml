import json
import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from branca.element import MacroElement
from jinja2 import Template
import pandas as pd

# Set Page Config
st.set_page_config(
    page_title="Peta Aksesibilitas Perguruan Tinggi Jabodetabek & Karawang",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling (Zero Emojis)
st.markdown("""
    <style>
    .main-header {
        font-family: 'Outfit', sans-serif;
        color: #2563EB;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        color: #64748B;
        font-size: 16px;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .context-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        line-height: 1.6;
    }
    .context-card strong {
        color: #60A5FA !important;
    }
    .analysis-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 5px solid #EF4444;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 18px;
        margin-bottom: 15px;
        color: #F8FAFC !important;
        font-size: 15px;
        line-height: 1.7;
        font-family: 'Inter', sans-serif;
    }
    .analysis-card strong {
        color: #60A5FA !important;
        font-weight: 700;
    }
    .analysis-card em {
        color: #F87171 !important;
        font-style: normal;
        font-weight: 600;
    }
    .sidebar-title {
        font-family: 'Outfit', sans-serif;
        color: #3B82F6;
        font-size: 18px;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .source-line {
        font-family: 'Inter', sans-serif;
        color: #9CA3AF;
        font-size: 12px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
    }
    .metric-card, .metric-card * {
        color: #F8FAFC !important;
    }
    .metric-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        opacity: 0.85;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
    }
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stCustomComponentV1"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    iframe {
        display: block;
        margin: 0 auto;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

import os

# Helper function to load geojson (auto-invalidates cache when file changes)
@st.cache_data(ttl=30)
def load_geojson(path, mtime=None):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_geojson(path):
    mtime = os.path.getmtime(path) if os.path.exists(path) else 0
    return load_geojson(path, mtime)

# Load data layers
try:
    kec_data = get_geojson("data_ready/Kecamatan_Batas_Kecil.geojson")
except Exception:
    kec_data = None

camp_data = get_geojson("data_ready/Campuses_WebGIS.geojson")
stat_data = get_geojson("data_ready/Stations_WebGIS.geojson")
tj_data   = get_geojson("data_ready/Halte_TransJakarta.geojson")

# Sidebar Controls
st.sidebar.markdown("<div class='sidebar-title'>Filter Kontrol</div>", unsafe_allow_html=True)

# Filter 1: Status Kampus
status_options = ["Semua", "PTN Only", "PTS Only"]
selected_status = st.sidebar.selectbox("Status Perguruan Tinggi", status_options)

# Filter 2: Kategori Aksesibilitas
kategori_options = ["Semua", "Transit-Oriented", "Transit-Isolated"]
selected_kategori = st.sidebar.selectbox("Kategori Aksesibilitas", kategori_options)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-title'>Tampilan Layer</div>", unsafe_allow_html=True)

show_kec     = st.sidebar.checkbox("Batas Kecamatan (Background)", value=True)
show_stat    = st.sidebar.checkbox("Stasiun KRL/MRT/LRT (Simpul Utama)", value=True)
show_tj      = st.sidebar.checkbox("Halte TransJakarta (Simpul Feeder)", value=True)
show_buffers = st.sidebar.checkbox("Radius Buffer (Transit-Oriented)", value=False)

# Parse campus features into a DataFrame for easier filtering and calculations
features = camp_data["features"]
rows = []
for idx, f in enumerate(features):
    props  = f["properties"]
    coords = f["geometry"]["coordinates"]
    rows.append({
        "index":     idx,
        "name":      props["name"],
        "status":    props["status"],
        "akreditasi":props["akreditasi"],
        "mahasiswa": props["mahasiswa"],
        "kategori":  props["kategori"],
        "dist_stat": props["dist_stat"],
        "dist_tj":   props["dist_tj"],
        "lon":       coords[0],
        "lat":       coords[1]
    })
df_camp = pd.DataFrame(rows)

# Apply filters
filtered_df = df_camp.copy()
if selected_status == "PTN Only":
    filtered_df = filtered_df[filtered_df["status"] == "PTN"]
elif selected_status == "PTS Only":
    filtered_df = filtered_df[filtered_df["status"] == "PTS"]

if selected_kategori == "Transit-Oriented":
    filtered_df = filtered_df[filtered_df["kategori"] == "Transit-Oriented"]
elif selected_kategori == "Transit-Isolated":
    filtered_df = filtered_df[filtered_df["kategori"] == "Transit-Isolated"]

# Dynamic Summary Metrics
total_filtered   = len(filtered_df)
oriented_count   = len(filtered_df[filtered_df["kategori"] == "Transit-Oriented"])
isolated_count   = len(filtered_df[filtered_df["kategori"] == "Transit-Isolated"])
oriented_pct     = (oriented_count / total_filtered * 100) if total_filtered > 0 else 0
isolated_pct     = (isolated_count / total_filtered * 100) if total_filtered > 0 else 0
isolated_students = filtered_df[filtered_df["kategori"] == "Transit-Isolated"]["mahasiswa"].sum()

# F2: Campus search — built from filtered results
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-title'>Cari Kampus</div>", unsafe_allow_html=True)
campus_names    = ["-- Semua --"] + sorted(filtered_df["name"].tolist())
selected_campus = st.sidebar.selectbox("Pilih Kampus", campus_names)

# Resolve map center and zoom based on campus search selection
DEFAULT_CENTER = [-6.25, 106.84]
DEFAULT_ZOOM   = 11
map_center     = DEFAULT_CENTER
map_zoom       = DEFAULT_ZOOM

selected_campus_row = None
if selected_campus != "-- Semua --" and total_filtered > 0:
    match = filtered_df[filtered_df["name"] == selected_campus]
    if not match.empty:
        r = match.iloc[0]
        map_center          = [r["lat"], r["lon"]]
        map_zoom            = 14
        selected_campus_row = r

# Main Dashboard layout
st.markdown("<h1 class='main-header'>Peta Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Sistem informasi geografis berbasis web untuk memetakan integrasi simpul transportasi utama dan feeder terhadap lokasi kampus.</p>", unsafe_allow_html=True)

# F3: Context block + data source citation
st.markdown("""
    <div class='context-card'>
    Peta ini mengklasifikasikan perguruan tinggi di wilayah Jabodetabek ke dalam dua kategori aksesibilitas:
    <strong>Transit-Oriented</strong> (dalam radius 1.000 m dari stasiun KRL/MRT/LRT atau 500 m dari halte TransJakarta)
    dan <strong>Transit-Isolated</strong> (di luar radius tersebut). Klasifikasi ini digunakan untuk mengidentifikasi
    kampus yang membutuhkan intervensi kebijakan transportasi feeder.
    </div>
""", unsafe_allow_html=True)
st.markdown("<p class='source-line'>Sumber data: BPS, OpenStreetMap / GTFS TransJakarta & KAI Commuter, survei data kampus mandiri.</p>", unsafe_allow_html=True)

st.divider()

# F1: Metric cards in main body (4-column row)
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.metric("Kampus Terfilter", f"{total_filtered}")
with mc2:
    st.metric("Transit-Oriented", f"{oriented_pct:.1f}%", delta=f"{oriented_count} kampus")
with mc3:
    st.metric("Transit-Isolated", f"{isolated_pct:.1f}%", delta=f"{isolated_count} kampus", delta_color="inverse")
with mc4:
    st.metric("Mahasiswa Terdampak", f"{isolated_students:,}")

# Leaflet Map setup — center and zoom are dynamic (F2)
m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB positron", control_scale=True)

# 1. Background Kecamatan layer
if show_kec and kec_data:
    folium.GeoJson(
        kec_data,
        name="Batas Kecamatan",
        style_function=lambda x: {
            "fillColor": "#3B82F6",
            "color":     "#2563EB",
            "weight":    1.2,
            "fillOpacity": 0.12,
            "dashArray": "4, 4"
        },
        highlight_function=lambda x: {
            "fillColor": "#2563EB",
            "color":     "#1D4ED8",
            "weight":    2.5,
            "fillOpacity": 0.35
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["KECAMATAN", "KAB_KOTA", "sma_grad", "area_km2"],
            aliases=["Kecamatan:", "Kab/Kota:", "Lulusan SMA:", "Luas Wilayah (km²):"],
            style="background-color: #1E293B; color: #F8FAFC; font-family: sans-serif; font-size: 12px; padding: 8px; border-radius: 4px;"
        )
    ).add_to(m)

# 2. Buffer Layers (Radius 1000m for rail stations)
if show_buffers:
    buffer_group = folium.FeatureGroup(name="Transit Buffer Zones")
    for s in stat_data["features"]:
        coords = s["geometry"]["coordinates"]
        folium.Circle(
            location=[coords[1], coords[0]],
            radius=1000,
            fill=True,
            color="#2563EB",
            weight=1,
            fill_color="#2563EB",
            fill_opacity=0.08,
            interactive=False
        ).add_to(buffer_group)
    buffer_group.add_to(m)

# 3. KRL/MRT/LRT Stations Layer
if show_stat:
    station_group = folium.FeatureGroup(name="Stasiun Kereta")
    for s in stat_data["features"]:
        coords = s["geometry"]["coordinates"]
        props  = s["properties"]
        mode   = props.get("mode", "KRL")
        name   = props.get("name", "Stasiun")

        color = "#2563EB"  # KRL Blue
        if mode == "MRT":
            color = "#1D4ED8"  # MRT Dark Blue
        elif mode == "LRT":
            color = "#3B82F6"  # LRT Light Blue

        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 13px; line-height: 1.4; width: 220px;'>
            <h4 style='margin: 0 0 5px 0; color: #1E3A8A;'>{name}</h4>
            <hr style='margin: 3px 0; border: 0; border-top: 1px solid #D1D5DB;'>
            <strong>Jenis Transportasi:</strong> Stasiun {mode}<br>
            <strong>Status Simpul:</strong> Simpul Utama (Transit Hub)
        </div>
        """
        folium.CircleMarker(
            location=[coords[1], coords[0]],
            radius=5.5,
            color="#FFFFFF",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Stasiun {name} ({mode})"
        ).add_to(station_group)
    station_group.add_to(m)

# 4. TransJakarta Stops Layer
if show_tj:
    tj_group = folium.FeatureGroup(name="Halte TransJakarta")
    for bs in tj_data["features"]:
        coords = bs["geometry"]["coordinates"]
        props  = bs["properties"]
        name   = props.get("name", "Halte")

        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 13px; line-height: 1.4; width: 200px;'>
            <h4 style='margin: 0 0 5px 0; color: #7C3AED;'>{name}</h4>
            <hr style='margin: 3px 0; border: 0; border-top: 1px solid #D1D5DB;'>
            <strong>Jaringan:</strong> TransJakarta<br>
            <strong>Status Simpul:</strong> Simpul Pengumpan (Feeder)
        </div>
        """
        folium.CircleMarker(
            location=[coords[1], coords[0]],
            radius=3.5,
            color="#FFFFFF",
            weight=0.8,
            fill=True,
            fill_color="#7C3AED",
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{name}"
        ).add_to(tj_group)
    tj_group.add_to(m)

# 5. Campuses Layer — selected campus gets yellow highlight ring (F2)
campus_group = folium.FeatureGroup(name="Perguruan Tinggi")
for _, row in filtered_df.iterrows():
    is_selected = (
        selected_campus_row is not None
        and row["name"] == selected_campus_row["name"]
    )

    color        = "#10B981" if row["kategori"] == "Transit-Oriented" else "#EF4444"
    border_color = "#059669" if row["kategori"] == "Transit-Oriented" else "#DC2626"

    radius   = 12.0 if is_selected else 7.0
    weight   = 3    if is_selected else 1.5
    b_color  = "#FACC15" if is_selected else border_color

    popup_html = f"""
    <table style='font-family: sans-serif; font-size: 12px; border-collapse: collapse; width: 260px; border: 1px solid #E5E7EB;'>
        <tr style='background-color: #1E3A8A; color: white;'>
            <th colspan='2' style='padding: 8px; text-align: left;'>{row['name']}</th>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Status</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB;'>{row['status']}</td>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Akreditasi</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB;'>{row['akreditasi']}</td>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Mahasiswa</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB;'>{row['mahasiswa']:,} Orang</td>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Aksesibilitas</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB; color: {color}; font-weight: bold;'>{row['kategori']}</td>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Jarak Stasiun</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB;'>{row['dist_stat']:.1f} m</td>
        </tr>
        <tr>
            <td style='padding: 6px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Jarak Halte TJ</td>
            <td style='padding: 6px; border: 1px solid #E5E7EB;'>{row['dist_tj']:.1f} m</td>
        </tr>
    </table>
    """
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=b_color,
        weight=weight,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"]
    ).add_to(campus_group)
campus_group.add_to(m)

# Add layer control to map
folium.LayerControl(position="topright").add_to(m)

# F4: Inject legend as a fixed overlay inside the folium map (bottom-right)
_legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed;
    bottom: 30px;
    right: 10px;
    z-index: 1000;
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: sans-serif;
    font-size: 12px;
    color: #F8FAFC;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    min-width: 195px;
">
    <div style="font-weight:700; font-size:13px; margin-bottom:10px; color:#F8FAFC;">Legenda Peta</div>
    <div style="margin-bottom:7px;">
        <span style="display:inline-block;width:12px;height:12px;background-color:#10B981;border-radius:50%;margin-right:8px;vertical-align:middle;"></span>
        <strong>Transit-Oriented</strong> (Akses Baik)
    </div>
    <div style="margin-bottom:7px;">
        <span style="display:inline-block;width:12px;height:12px;background-color:#EF4444;border-radius:50%;margin-right:8px;vertical-align:middle;"></span>
        <strong>Transit-Isolated</strong> (Akses Buruk)
    </div>
    <div style="margin-bottom:7px;">
        <span style="display:inline-block;width:10px;height:10px;background-color:#2563EB;border-radius:50%;margin-right:8px;vertical-align:middle;"></span>
        <strong>Stasiun Kereta</strong> (KRL/MRT/LRT)
    </div>
    <div>
        <span style="display:inline-block;width:8px;height:8px;background-color:#7C3AED;border-radius:50%;margin-right:8px;vertical-align:middle;"></span>
        <strong>Halte TransJakarta</strong> (Feeder)
    </div>
</div>
{% endmacro %}
"""

class _LegendOverlay(MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template(_legend_html)

m.get_root().add_child(_LegendOverlay())

# F4: Full-width map render (no column split)
st_folium(m, use_container_width=True, height=620, returned_objects=[])

def generate_dynamic_analysis(df_filtered, df_all, selected_status, selected_kategori, selected_campus):
    # Tier 1: Specific Campus Search Selected
    if selected_campus != "-- Semua --":
        match = df_all[df_all["name"] == selected_campus]
        if not match.empty:
            r = match.iloc[0]
            kat = r["kategori"]
            status_full = "Perguruan Tinggi Negeri (PTN)" if r["status"] == "PTN" else "Perguruan Tinggi Swasta (PTS)"
            stat_dist = r["dist_stat"]
            tj_dist   = r["dist_tj"]
            
            if kat == "Transit-Oriented":
                nearest_desc = f"stasiun kereta ({stat_dist:.0f} m)" if stat_dist <= 1000 else f"halte TransJakarta ({tj_dist:.0f} m)"
                analysis_body = (
                    f"Kampus ini tergolong <em>Transit-Oriented</em> karena berada dalam jangkauan berjalan kaki "
                    f"atau akses mudah ke {nearest_desc}. Integrasi ini memberikan efisiensi mobilitas tinggi "
                    f"bagi <strong>{r['mahasiswa']:,} mahasiswa</strong> aktif."
                )
            else:
                analysis_body = (
                    f"Kampus ini berstatus <em>Transit-Isolated</em> dengan jarak <strong>{stat_dist:,.0f} m</strong> "
                    f"ke stasiun kereta terdekat dan <strong>{tj_dist:,.0f} m</strong> ke halte TransJakarta. "
                    f"Diperlukan fasilitas feeder angkutan umum langsung untuk melayani <strong>{r['mahasiswa']:,} mahasiswa</strong> di lokasi ini."
                )
            
            return f"""
            <div class='analysis-card'>
                <strong style='font-size:16px; display:block; margin-bottom:6px;'>Analisis Spasial: {r['name']}</strong>
                <div>Status: {status_full} | Akreditasi: {r['akreditasi']} | Pop. Mahasiswa: {r['mahasiswa']:,} orang</div>
                <hr style='border:0; border-top:1px solid #334155; margin:8px 0;'>
                {analysis_body}
            </div>
            """
    
    total = len(df_filtered)
    if total == 0:
        return "<div class='analysis-card'>Tidak ada data kampus yang memenuhi kriteria filter aktif.</div>"
        
    oriented_cnt = len(df_filtered[df_filtered["kategori"] == "Transit-Oriented"])
    isolated_cnt = len(df_filtered[df_filtered["kategori"] == "Transit-Isolated"])
    oriented_pct = (oriented_cnt / total) * 100
    isolated_pct = (isolated_cnt / total) * 100
    total_students = df_filtered["mahasiswa"].sum()
    isolated_students = df_filtered[df_filtered["kategori"] == "Transit-Isolated"]["mahasiswa"].sum()
    
    # Tier 2: Status Filter (PTN / PTS)
    if selected_status == "PTN Only":
        return f"""
        <div class='analysis-card'>
            <strong style='font-size:16px; display:block; margin-bottom:6px;'>Analisis Kelompok Perguruan Tinggi Negeri (PTN)</strong>
            Dari total <strong>{total} kampus PTN</strong> di Jabodetabek & Karawang, sebanyak <strong>{oriented_cnt} kampus ({oriented_pct:.1f}%)</strong> berstatus <em>Transit-Oriented</em> dan <strong>{isolated_cnt} kampus ({isolated_pct:.1f}%)</strong> berstatus <em>Transit-Isolated</em>.
            Kampus utama PTN (seperti UI Depok dan UNJ Rawamangun) terintegrasi langsung dengan koridor utama rel KRL, sedangkan kampus vokasi/satelit di kawasan pinggiran masih membutuhkan rute feeder tambahan untuk <strong>{isolated_students:,} mahasiswa</strong>.
        </div>
        """
    elif selected_status == "PTS Only":
        return f"""
        <div class='analysis-card'>
            <strong style='font-size:16px; display:block; margin-bottom:6px;'>Analisis Kelompok Perguruan Tinggi Swasta (PTS)</strong>
            Sektor swasta mendominasi lanskap perguruan tinggi dengan <strong>{total} kampus</strong> dan total <strong>{total_students:,} mahasiswa</strong>.
            Sebanyak <strong>{isolated_cnt} kampus PTS ({isolated_pct:.1f}%)</strong> tergolong <em>Transit-Isolated</em>, yang berdampak pada <strong>{isolated_students:,} mahasiswa</strong>. Ekspansi kampus PTS di kawasan penyangga (Tangerang, Bekasi, Karawang) yang jauh dari jalur rel menjadi penggerak utama ketergantungan pada kendaraan pribadi.
        </div>
        """
        
    # Tier 3: Kategori Filter
    if selected_kategori == "Transit-Oriented":
        return f"""
        <div class='analysis-card'>
            <strong style='font-size:16px; display:block; margin-bottom:6px;'>Analisis Kelompok Transit-Oriented (Akses Baik)</strong>
            Terdapat <strong>{oriented_cnt} kampus ({oriented_pct:.1f}%)</strong> yang berada dalam radius pelayanan langsung angkutan massal (<= 1.000m dari stasiun kereta atau <= 500m dari halte TransJakarta).
            Kelompok ini melayani <strong>{total_students:,} mahasiswa</strong> dengan tingkat aksesibilitas multimoda yang optimal.
        </div>
        """
    elif selected_kategori == "Transit-Isolated":
        return f"""
        <div class='analysis-card'>
            <strong style='font-size:16px; display:block; margin-bottom:6px;'>Analisis Kelompok Transit-Isolated (Akses Terbatas)</strong>
            Terdapat <strong>{isolated_cnt} kampus ({isolated_pct:.1f}%)</strong> yang berada di luar radius akses langsung stasiun maupun halte feeder.
            Kondisi ini berdampak langsung pada <strong>{isolated_students:,} mahasiswa</strong>, mengindikasikan prioritas tinggi untuk intervensi integrasi rute bus pengumpan regional.
        </div>
        """
        
    # Tier 4: Neutral Default Overview
    return f"""
    <div class='analysis-card'>
        <strong style='font-size:16px; display:block; margin-bottom:6px;'>Ringkasan Integrasi Aksesibilitas Transportasi Massal</strong>
        Pemetaan mencakup <strong>{total} perguruan tinggi</strong> di wilayah Jabodetabek dan Karawang dengan total <strong>{total_students:,} mahasiswa</strong>.
        Hasil evaluasi menunjukkan <strong>{oriented_cnt} kampus ({oriented_pct:.1f}%)</strong> memiliki aksesibilitas <em>Transit-Oriented</em>, sementara <strong>{isolated_cnt} kampus ({isolated_pct:.1f}%)</strong> tergolong <em>Transit-Isolated</em>. Gunakan filter kontrol di sidebar untuk mengeksplorasi rincian menurut status kelembagaan maupun nama kampus spesifik.
    </div>
    """

# Analysis text below map (Dynamic rendering)
st.markdown(generate_dynamic_analysis(filtered_df, df_camp, selected_status, selected_kategori, selected_campus), unsafe_allow_html=True)

# F5: Filtered campus data table
if total_filtered > 0:
    st.divider()
    st.caption(f"Menampilkan {total_filtered} kampus sesuai filter aktif")
    display_df = filtered_df[["name", "status", "akreditasi", "mahasiswa", "kategori", "dist_stat", "dist_tj"]].copy()
    display_df = display_df.rename(columns={
        "name":      "Perguruan Tinggi",
        "status":    "Status",
        "akreditasi":"Akreditasi",
        "mahasiswa": "Mahasiswa",
        "kategori":  "Aksesibilitas",
        "dist_stat": "Jarak Stasiun (m)",
        "dist_tj":   "Jarak Halte TJ (m)"
    })
    display_df["Jarak Stasiun (m)"] = display_df["Jarak Stasiun (m)"].round(0).astype(int)
    display_df["Jarak Halte TJ (m)"] = display_df["Jarak Halte TJ (m)"].round(0).astype(int)
    display_df = display_df.sort_values("Jarak Stasiun (m)").reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
