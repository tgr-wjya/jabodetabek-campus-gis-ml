import json
import streamlit as st
import folium
from streamlit_folium import folium_static
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
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        color: #4B5563;
        font-size: 16px;
        margin-bottom: 25px;
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
    .legend-container {
        padding: 12px;
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        font-size: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .legend-container, .legend-container * {
        color: #F8FAFC !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to load geojson
@st.cache_data
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load data layers
try:
    kec_data = load_geojson("data_ready/Kecamatan_Batas_Kecil.geojson")
except Exception:
    kec_data = None

camp_data = load_geojson("data_ready/Campuses_WebGIS.geojson")
stat_data = load_geojson("data_ready/Stations_WebGIS.geojson")
tj_data = load_geojson("data_ready/Halte_TransJakarta.geojson")

# Sidebar Controls
st.sidebar.markdown("<h2 style='color:#1E3A8A;'>Filter Kontrol</h2>", unsafe_allow_html=True)

# Filter 1: Status Kampus
status_options = ["Semua", "PTN Only", "PTS Only"]
selected_status = st.sidebar.selectbox("Status Perguruan Tinggi", status_options)

# Filter 2: Kategori Aksesibilitas
kategori_options = ["Semua", "Transit-Oriented", "Transit-Isolated"]
selected_kategori = st.sidebar.selectbox("Kategori Aksesibilitas", kategori_options)

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#1E3A8A;'>Tampilan Layer</h3>", unsafe_allow_html=True)

show_kec = st.sidebar.checkbox("Batas Kecamatan (Background)", value=True)
show_stat = st.sidebar.checkbox("Stasiun KRL/MRT/LRT (Simpul Utama)", value=True)
show_tj = st.sidebar.checkbox("Halte TransJakarta (Simpul Feeder)", value=True)
show_buffers = st.sidebar.checkbox("Radius Buffer (Transit-Oriented)", value=False)

# Parse campus features into a DataFrame for easier filtering and calculations
features = camp_data["features"]
rows = []
for idx, f in enumerate(features):
    props = f["properties"]
    coords = f["geometry"]["coordinates"]
    rows.append({
        "index": idx,
        "name": props["name"],
        "status": props["status"],
        "akreditasi": props["akreditasi"],
        "mahasiswa": props["mahasiswa"],
        "kategori": props["kategori"],
        "dist_stat": props["dist_stat"],
        "dist_tj": props["dist_tj"],
        "lon": coords[0],
        "lat": coords[1]
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
total_filtered = len(filtered_df)
oriented_count = len(filtered_df[filtered_df["kategori"] == "Transit-Oriented"])
isolated_count = len(filtered_df[filtered_df["kategori"] == "Transit-Isolated"])
oriented_pct = (oriented_count / total_filtered * 100) if total_filtered > 0 else 0
isolated_pct = (isolated_count / total_filtered * 100) if total_filtered > 0 else 0
isolated_students = filtered_df[filtered_df["kategori"] == "Transit-Isolated"]["mahasiswa"].sum()

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#1E3A8A;'>Ringkasan Eksekutif</h3>", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class='metric-card'>
    <div class='metric-title'>Jumlah Kampus Terfilter</div>
    <div class='metric-value'>{total_filtered} Kampus</div>
</div>
<div class='metric-card' style='border-left-color: #10B981;'>
    <div class='metric-title'>Transit-Oriented (Akses Baik)</div>
    <div class='metric-value'>{oriented_pct:.1f}%</div>
    <div style='font-size: 12px; color: #4B5563;'>{oriented_count} kampus dekat stasiun/halte</div>
</div>
<div class='metric-card' style='border-left-color: #EF4444;'>
    <div class='metric-title'>Transit-Isolated (Akses Buruk)</div>
    <div class='metric-value'>{isolated_pct:.1f}%</div>
    <div style='font-size: 12px; color: #4B5563;'>{isolated_count} kampus membutuhkan angkutan feeder</div>
</div>
<div class='metric-card' style='border-left-color: #F59E0B;'>
    <div class='metric-title'>Estimasi Mahasiswa Terdampak</div>
    <div class='metric-value'>{isolated_students:,} Orang</div>
    <div style='font-size: 12px; color: #4B5563;'>Bergantung pada akses jalan kaki jauh / angkutan informal</div>
</div>
""", unsafe_allow_html=True)

# Main Dashboard layout
st.markdown("<h1 class='main-header'>Peta Aksesibilitas Transportasi Massal Perguruan Tinggi Jabodetabek</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Sistem informasi geografis berbasis web untuk memetakan integrasi simpul transportasi utama dan feeder terhadap lokasi kampus.</p>", unsafe_allow_html=True)

# Leaflet Map setup
map_center = [-6.2088, 106.8456] # Jakarta center
m = folium.Map(location=map_center, zoom_start=11, tiles="CartoDB positron", control_scale=True)

# 1. Background Kecamatan layer
if show_kec and kec_data:
    folium.GeoJson(
        kec_data,
        name="Batas Kecamatan",
        style_function=lambda x: {
            "fillColor": "#F3F4F6",
            "color": "#9CA3AF",
            "weight": 0.8,
            "fillOpacity": 0.3
        },
        tooltip=folium.GeoJsonTooltip(fields=["KECAMATAN", "KAB_KOTA"], aliases=["Kecamatan:", "Kab/Kota:"])
    ).add_to(m)

# 2. Buffer Layers (Radius 1000m for rail stations, 500m for bus stops)
if show_buffers:
    buffer_group = folium.FeatureGroup(name="Transit Buffer Zones")
    
    # We only draw buffers for stations to optimize rendering
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
        props = s["properties"]
        mode = props.get("mode", "KRL")
        name = props.get("name", "Stasiun")
        
        # Color based on mode
        color = "#2563EB" # KRL Blue
        if mode == "MRT":
            color = "#1D4ED8" # MRT Dark Blue
        elif mode == "LRT":
            color = "#3B82F6" # LRT Light Blue
            
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
    # For performance, we render TJ stops as smaller points
    for bs in tj_data["features"]:
        coords = bs["geometry"]["coordinates"]
        props = bs["properties"]
        name = props.get("name", "Halte")
        
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
            fill_color="#7C3AED", # Purple
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{name}"
        ).add_to(tj_group)
    tj_group.add_to(m)

# 5. Campuses Layer
campus_group = folium.FeatureGroup(name="Perguruan Tinggi")
for _, row in filtered_df.iterrows():
    # Green if Transit-Oriented, Red/Orange if Transit-Isolated
    color = "#10B981" if row["kategori"] == "Transit-Oriented" else "#EF4444"
    border_color = "#059669" if row["kategori"] == "Transit-Oriented" else "#DC2626"
    
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
        radius=7.0,
        color=border_color,
        weight=1.5,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"]
    ).add_to(campus_group)
campus_group.add_to(m)

# Add layer control to map
folium.LayerControl(position="topright").add_to(m)

# Layout: Map rendering in main column
col_map, col_details = st.columns([4, 1])

with col_map:
    folium_static(m, width=950, height=600)

with col_details:
    st.markdown("<h4 style='color:#1E3A8A;'>Legenda Peta</h4>", unsafe_allow_html=True)
    st.markdown("""
        <div class='legend-container'>
            <div style='margin-bottom: 8px;'>
                <span style='display:inline-block; width:12px; height:12px; background-color:#10B981; border-radius:50%; margin-right:8px;'></span>
                <strong>Transit-Oriented</strong> (Akses Baik)
            </div>
            <div style='margin-bottom: 8px;'>
                <span style='display:inline-block; width:12px; height:12px; background-color:#EF4444; border-radius:50%; margin-right:8px;'></span>
                <strong>Transit-Isolated</strong> (Akses Buruk)
            </div>
            <div style='margin-bottom: 8px;'>
                <span style='display:inline-block; width:10px; height:10px; background-color:#2563EB; border-radius:50%; margin-right:8px;'></span>
                <strong>Stasiun Kereta</strong> (KRL/MRT/LRT)
            </div>
            <div style='margin-bottom: 8px;'>
                <span style='display:inline-block; width:8px; height:8px; background-color:#7C3AED; border-radius:50%; margin-right:8px;'></span>
                <strong>Halte TransJakarta</strong> (Feeder)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h4 style='color:#1E3A8A; margin-top:20px;'>Analisis Akses</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='font-size: 13px; line-height: 1.5;'>
            Berdasarkan klasifikasi radius pelayanan transportasi, terdapat 
            <strong>{isolated_count} kampus ({isolated_pct:.1f}%)</strong> yang berstatus 
            <em>Transit-Isolated</em>. Kampus-kampus ini berada lebih dari 1.000 meter dari stasiun KRL/MRT/LRT 
            dan lebih dari 500 meter dari halte TransJakarta. Hal ini berdampak langsung pada 
            <strong>{isolated_students:,} mahasiswa</strong> yang berkuliah di lokasi-lokasi tersebut, sehingga 
            mereka sangat bergantung pada angkutan informal atau kendaraan pribadi.
        </div>
    """, unsafe_allow_html=True)
