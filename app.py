import json
import os
import time

import altair as alt
import folium
import numpy as np
import pandas as pd
import streamlit as st
from branca.element import MacroElement
from jinja2 import Template
from sklearn.ensemble import RandomForestClassifier
from streamlit_folium import st_folium

# Record script execution start time for server latency measurement
t_start = time.perf_counter()

# Set Page Config
st.set_page_config(
    page_title="WebGIS Aksesibilitas & Sistem Rekomendasi Kampus Jabodetabek",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark styling (Zero Emojis, 100% Bahasa Indonesia)
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@600;700&display=swap" rel="stylesheet">
    <style>
    @font-face {
        font-family: 'Outfit';
        font-display: swap;
    }
    @font-face {
        font-family: 'Inter';
        font-display: swap;
    }
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
        font-size: 15px;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .context-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
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
        font-size: 14px;
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
    .reko-card-green {
        background-color: #064E3B;
        border: 1px solid #059669;
        border-radius: 8px;
        padding: 14px;
        color: #ECFDF5;
        font-weight: 600;
    }
    .reko-card-yellow {
        background-color: #78350F;
        border: 1px solid #D97706;
        border-radius: 8px;
        padding: 14px;
        color: #FEF3C7;
        font-weight: 600;
    }
    .reko-card-red {
        background-color: #7F1D1D;
        border: 1px solid #DC2626;
        border-radius: 8px;
        padding: 14px;
        color: #FEE2E2;
        font-weight: 600;
    }
    .sidebar-title {
        font-family: 'Outfit', sans-serif;
        color: #3B82F6;
        font-size: 17px;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .source-line {
        font-family: 'Inter', sans-serif;
        color: #9CA3AF;
        font-size: 12px;
        margin-bottom: 15px;
    }
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
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
    .latency-footer {
        text-align: center;
        color: #94A3B8;
        font-size: 12px;
        margin-top: 25px;
        padding-top: 10px;
        border-top: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# Cache GeoJSON data loading
@st.cache_data(ttl=3600)
def load_geojson(path, mtime=None):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_geojson(path):
    mtime = os.path.getmtime(path) if os.path.exists(path) else 0
    return load_geojson(path, mtime)

# Load data layers
kec_data  = get_geojson("data_ready/Kecamatan_ML_Simplified.geojson")
camp_data = get_geojson("data_ready/Campuses_WebGIS.geojson")
stat_data = get_geojson("data_ready/Stations_WebGIS.geojson")
tj_data   = get_geojson("data_ready/Halte_TransJakarta.geojson")

@st.cache_data(ttl=3600)
def load_predictions():
    return pd.read_csv("data_ready/kecamatan_predictions.csv")

df_pred = load_predictions()

# Train Random Forest Model once for live interactive simulator in Tab 2
@st.cache_resource
def get_trained_rf_model(df):
    feature_cols = ["dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2"]
    X = df[feature_cols].values
    y = df["Label_Reko"].values
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
    rf.fit(X, y)
    return rf

rf_model = get_trained_rf_model(df_pred)

# Main Application Title
st.markdown("<h1 class='main-header'>WebGIS Sistem Informasi Geografis Perguruan Tinggi Jabodetabek & Karawang</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Platform interaktif pemetaan aksesibilitas transportasi massal (Soal 1) dan sistem rekomendasi lokasi kampus satelit berbasis Machine Learning Random Forest (Soal 2).</p>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2 = st.tabs([
    "Soal 1: Peta Aksesibilitas Transportasi Massal",
    "Soal 2: Sistem Rekomendasi Kampus Satelit (ML Random Forest)"
])

# ==============================================================================
# TAB 1: SOAL 1 - PETA AKSESIBILITAS TRANSPORTASI MASSAL
# ==============================================================================
with tab1:
    st.markdown("""
        <div class='context-card'>
        <strong>Modul Soal 1:</strong> Mengklasifikasikan 266 perguruan tinggi di wilayah Jabodetabek & Karawang ke dalam dua kategori aksesibilitas:
        <strong>Transit-Oriented</strong> (radius <= 1.000m dari stasiun KRL/MRT/LRT atau <= 500m dari halte TransJakarta)
        dan <strong>Transit-Isolated</strong> (di luar radius akses langsung).
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p class='source-line'>Sumber data: BPS, OpenStreetMap / GTFS TransJakarta & KAI Commuter, PDDikti Kemdikbudristek.</p>", unsafe_allow_html=True)

    # Parse campus features into a DataFrame
    camp_rows = []
    for idx, f in enumerate(camp_data["features"]):
        props  = f["properties"]
        coords = f["geometry"]["coordinates"]
        camp_rows.append({
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
    df_camp = pd.DataFrame(camp_rows)

    # Sidebar Filter Controls for Tab 1
    st.sidebar.markdown("<div class='sidebar-title'>Filter Tab 1: Aksesibilitas</div>", unsafe_allow_html=True)
    status_options = ["Semua", "PTN Only", "PTS Only"]
    selected_status = st.sidebar.selectbox("Status Perguruan Tinggi", status_options, key="t1_status")

    kategori_options = ["Semua", "Transit-Oriented", "Transit-Isolated"]
    selected_kategori = st.sidebar.selectbox("Kategori Aksesibilitas", kategori_options, key="t1_kategori")

    show_kec     = st.sidebar.checkbox("Batas Kecamatan (Optimized GeoJSON)", value=True, key="t1_kec")
    show_stat    = st.sidebar.checkbox("Stasiun KRL/MRT/LRT (Simpul Utama)", value=True, key="t1_stat")
    show_tj      = st.sidebar.checkbox("Halte TransJakarta (Simpul Feeder)", value=True, key="t1_tj")
    show_buffers = st.sidebar.checkbox("Radius Buffer (Transit-Oriented)", value=False, key="t1_buf")

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

    # Campus Search Selection
    campus_names    = ["-- Semua --"] + sorted(filtered_df["name"].tolist())
    selected_campus = st.sidebar.selectbox("Cari Nama Kampus Spesifik", campus_names, key="t1_campus")

    DEFAULT_CENTER = [-6.25, 106.84]
    DEFAULT_ZOOM   = 11
    map_center     = DEFAULT_CENTER
    map_zoom       = DEFAULT_ZOOM

    selected_campus_row = None
    if selected_campus != "-- Semua --" and len(filtered_df) > 0:
        match = filtered_df[filtered_df["name"] == selected_campus]
        if not match.empty:
            r = match.iloc[0]
            map_center          = [r["lat"], r["lon"]]
            map_zoom            = 14
            selected_campus_row = r

    # Metrics Summary Row
    total_filtered    = len(filtered_df)
    oriented_count    = len(filtered_df[filtered_df["kategori"] == "Transit-Oriented"])
    isolated_count    = len(filtered_df[filtered_df["kategori"] == "Transit-Isolated"])
    oriented_pct      = (oriented_count / total_filtered * 100) if total_filtered > 0 else 0
    isolated_pct      = (isolated_count / total_filtered * 100) if total_filtered > 0 else 0
    isolated_students = filtered_df[filtered_df["kategori"] == "Transit-Isolated"]["mahasiswa"].sum()

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("Kampus Terfilter", f"{total_filtered}")
    with mc2:
        st.metric("Transit-Oriented", f"{oriented_pct:.1f}%", delta=f"{oriented_count} Kampus")
    with mc3:
        st.metric("Transit-Isolated", f"{isolated_pct:.1f}%", delta=f"{isolated_count} Kampus", delta_color="inverse")
    with mc4:
        st.metric("Mahasiswa Terdampak", f"{isolated_students:,}")

    # Folium Leaflet Map Setup for Tab 1
    m1 = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB positron", control_scale=True)

    if show_kec and kec_data:
        folium.GeoJson(
            kec_data,
            name="Batas Kecamatan",
            style_function=lambda x: {
                "fillColor": "#3B82F6",
                "color":     "#2563EB",
                "weight":    1.0,
                "fillOpacity": 0.08,
                "dashArray": "3, 3"
            },
            highlight_function=lambda x: {
                "fillColor": "#2563EB",
                "color":     "#1D4ED8",
                "weight":    2.0,
                "fillOpacity": 0.25
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["KECAMATAN", "KAB_KOTA", "sma_grad", "area_km2"],
                aliases=["Kecamatan:", "Kab/Kota:", "Lulusan SMA:", "Luas Wilayah (km2):"],
                style="background-color: #1E293B; color: #F8FAFC; font-family: sans-serif; font-size: 12px; padding: 6px; border-radius: 4px;"
            )
        ).add_to(m1)

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
        buffer_group.add_to(m1)

    if show_stat:
        station_group = folium.FeatureGroup(name="Stasiun Kereta")
        for s in stat_data["features"]:
            coords = s["geometry"]["coordinates"]
            props  = s["properties"]
            mode   = props.get("mode", "KRL")
            name   = props.get("name", "Stasiun")

            color = "#2563EB"
            if mode == "MRT":
                color = "#1D4ED8"
            elif mode == "LRT":
                color = "#3B82F6"

            popup_html = f"""
            <div style='font-family: sans-serif; font-size: 12px; line-height: 1.4; width: 220px;'>
                <h4 style='margin: 0 0 5px 0; color: #1E3A8A;'>{name}</h4>
                <hr style='margin: 3px 0; border: 0; border-top: 1px solid #D1D5DB;'>
                <strong>Jenis Transportasi:</strong> Stasiun {mode}<br>
                <strong>Status Simpul:</strong> Simpul Utama (Transit Hub)
            </div>
            """
            folium.CircleMarker(
                location=[coords[1], coords[0]],
                radius=5.0,
                color="#FFFFFF",
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.9,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Stasiun {name} ({mode})"
            ).add_to(station_group)
        station_group.add_to(m1)

    if show_tj:
        tj_group = folium.FeatureGroup(name="Halte TransJakarta")
        for bs in tj_data["features"]:
            coords = bs["geometry"]["coordinates"]
            props  = bs["properties"]
            name   = props.get("name", "Halte")

            popup_html = f"""
            <div style='font-family: sans-serif; font-size: 12px; line-height: 1.4; width: 200px;'>
                <h4 style='margin: 0 0 5px 0; color: #7C3AED;'>{name}</h4>
                <hr style='margin: 3px 0; border: 0; border-top: 1px solid #D1D5DB;'>
                <strong>Jaringan:</strong> TransJakarta<br>
                <strong>Status Simpul:</strong> Simpul Pengumpan (Feeder)
            </div>
            """
            folium.CircleMarker(
                location=[coords[1], coords[0]],
                radius=3.0,
                color="#FFFFFF",
                weight=0.8,
                fill=True,
                fill_color="#7C3AED",
                fill_opacity=0.8,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{name}"
            ).add_to(tj_group)
        tj_group.add_to(m1)

    campus_group = folium.FeatureGroup(name="Perguruan Tinggi")
    for _, row in filtered_df.iterrows():
        is_selected = (selected_campus_row is not None and row["name"] == selected_campus_row["name"])
        color        = "#10B981" if row["kategori"] == "Transit-Oriented" else "#EF4444"
        border_color = "#059669" if row["kategori"] == "Transit-Oriented" else "#DC2626"
        radius   = 11.0 if is_selected else 6.5
        weight   = 3    if is_selected else 1.5
        b_color  = "#FACC15" if is_selected else border_color

        popup_html = f"""
        <table style='font-family: sans-serif; font-size: 12px; border-collapse: collapse; width: 250px; border: 1px solid #E5E7EB;'>
            <tr style='background-color: #1E3A8A; color: white;'>
                <th colspan='2' style='padding: 6px; text-align: left;'>{row['name']}</th>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Status</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB;'>{row['status']}</td>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Akreditasi</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB;'>{row['akreditasi']}</td>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Mahasiswa</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB;'>{row['mahasiswa']:,} Orang</td>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Aksesibilitas</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB; color: {color}; font-weight: bold;'>{row['kategori']}</td>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Jarak Stasiun</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB;'>{row['dist_stat']:.1f} m</td>
            </tr>
            <tr>
                <td style='padding: 5px; border: 1px solid #E5E7EB; font-weight: bold; background-color: #F9FAFB;'>Jarak Halte TJ</td>
                <td style='padding: 5px; border: 1px solid #E5E7EB;'>{row['dist_tj']:.1f} m</td>
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
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=row["name"]
        ).add_to(campus_group)
    campus_group.add_to(m1)

    folium.LayerControl(position="topright").add_to(m1)

    # Inject Legend for Tab 1 Map
    _legend_html1 = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 25px;
        right: 10px;
        z-index: 1000;
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 14px;
        font-family: sans-serif;
        font-size: 12px;
        color: #F8FAFC;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        min-width: 185px;
    ">
        <div style="font-weight:700; font-size:12px; margin-bottom:8px; color:#F8FAFC;">Legenda Peta Aksesibilitas</div>
        <div style="margin-bottom:6px;">
            <span style="display:inline-block;width:11px;height:11px;background-color:#10B981;border-radius:50%;margin-right:7px;vertical-align:middle;"></span>
            <strong>Transit-Oriented</strong> (Akses Baik)
        </div>
        <div style="margin-bottom:6px;">
            <span style="display:inline-block;width:11px;height:11px;background-color:#EF4444;border-radius:50%;margin-right:7px;vertical-align:middle;"></span>
            <strong>Transit-Isolated</strong> (Akses Terbatas)
        </div>
        <div style="margin-bottom:6px;">
            <span style="display:inline-block;width:9px;height:9px;background-color:#2563EB;border-radius:50%;margin-right:7px;vertical-align:middle;"></span>
            <strong>Stasiun Kereta</strong> (KRL/MRT/LRT)
        </div>
        <div>
            <span style="display:inline-block;width:8px;height:8px;background-color:#7C3AED;border-radius:50%;margin-right:7px;vertical-align:middle;"></span>
            <strong>Halte TransJakarta</strong> (Feeder)
        </div>
    </div>
    {% endmacro %}
    """

    class _LegendOverlay1(MacroElement):
        def __init__(self):
            super().__init__()
            self._template = Template(_legend_html1)

    m1.get_root().add_child(_LegendOverlay1())
    st_folium(m1, use_container_width=True, height=580, returned_objects=[], key="map_tab1")

    # 4-Tier Analysis Card Text
    def generate_t1_analysis(df_filt, df_all, sel_status, sel_kat, sel_camp):
        if sel_camp != "-- Semua --":
            match = df_all[df_all["name"] == sel_camp]
            if not match.empty:
                r = match.iloc[0]
                kat = r["kategori"]
                status_full = "Perguruan Tinggi Negeri (PTN)" if r["status"] == "PTN" else "Perguruan Tinggi Swasta (PTS)"
                stat_dist = r["dist_stat"]
                tj_dist   = r["dist_tj"]
                if kat == "Transit-Oriented":
                    nearest_desc = f"stasiun kereta ({stat_dist:.0f} m)" if stat_dist <= 1000 else f"halte TransJakarta ({tj_dist:.0f} m)"
                    body = f"Kampus ini tergolong <em>Transit-Oriented</em> karena berada dalam jangkauan ke {nearest_desc}, memberikan efisiensi mobilitas bagi <strong>{r['mahasiswa']:,} mahasiswa</strong>."
                else:
                    body = f"Kampus ini berstatus <em>Transit-Isolated</em> dengan jarak <strong>{stat_dist:,.0f} m</strong> ke stasiun kereta dan <strong>{tj_dist:,.0f} m</strong> ke halte TransJakarta, membutuhkan rute feeder untuk <strong>{r['mahasiswa']:,} mahasiswa</strong>."
                return f"<div class='analysis-card'><strong style='font-size:15px;'>Analisis Kampus: {r['name']}</strong><br>Status: {status_full} | Akreditasi: {r['akreditasi']} | Mahasiswa: {r['mahasiswa']:,} orang<hr style='border:0; border-top:1px solid #334155; margin:6px 0;'>{body}</div>"

        total = len(df_filt)
        if total == 0:
            return "<div class='analysis-card'>Tidak ada data kampus yang memenuhi kriteria filter aktif.</div>"
        
        oriented_cnt = len(df_filt[df_filt["kategori"] == "Transit-Oriented"])
        isolated_cnt = len(df_filt[df_filt["kategori"] == "Transit-Isolated"])
        oriented_pct = (oriented_cnt / total) * 100
        isolated_pct = (isolated_cnt / total) * 100
        tot_students = df_filt["mahasiswa"].sum()
        iso_students = df_filt[df_filt["kategori"] == "Transit-Isolated"]["mahasiswa"].sum()

        if sel_status == "PTN Only":
            return f"<div class='analysis-card'><strong style='font-size:15px;'>Analisis Kelompok Perguruan Tinggi Negeri (PTN)</strong><br>Dari total <strong>{total} kampus PTN</strong>, sebanyak <strong>{oriented_cnt} kampus ({oriented_pct:.1f}%)</strong> berstatus <em>Transit-Oriented</em> dan <strong>{isolated_cnt} kampus ({isolated_pct:.1f}%)</strong> berstatus <em>Transit-Isolated</em>. Kampus utama PTN terintegrasi koridor utama rel KRL, sedangkan kampus vokasi/satelit pinggiran membutuhkan rute pengumpan untuk <strong>{iso_students:,} mahasiswa</strong>.</div>"
        elif sel_status == "PTS Only":
            return f"<div class='analysis-card'><strong style='font-size:15px;'>Analisis Kelompok Perguruan Tinggi Swasta (PTS)</strong><br>Sektor swasta mendominasi dengan <strong>{total} kampus</strong> dan <strong>{tot_students:,} mahasiswa</strong>. Sebanyak <strong>{isolated_cnt} kampus PTS ({isolated_pct:.1f}%)</strong> tergolong <em>Transit-Isolated</em>, berdampak pada <strong>{iso_students:,} mahasiswa</strong> akibat pola ekspansi kampus swasta di kawasan penyangga jauh dari jalur rel.</div>"
        
        return f"<div class='analysis-card'><strong style='font-size:15px;'>Ringkasan Integrasi Aksesibilitas Transportasi Massal</strong><br>Pemetaan mencakup <strong>{total} perguruan tinggi</strong> di wilayah Jabodetabek & Karawang ({tot_students:,} mahasiswa). Sebanyak <strong>{oriented_cnt} kampus ({oriented_pct:.1f}%)</strong> tergolong <em>Transit-Oriented</em>, sedangkan <strong>{isolated_cnt} kampus ({isolated_pct:.1f}%)</strong> tergolong <em>Transit-Isolated</em>.</div>"

    st.markdown(generate_t1_analysis(filtered_df, df_camp, selected_status, selected_kategori, selected_campus), unsafe_allow_html=True)

    if total_filtered > 0:
        st.divider()
        st.caption(f"Tabel Data Perguruan Tinggi Terfilter ({total_filtered} Kampus)")
        disp_df = filtered_df[["name", "status", "akreditasi", "mahasiswa", "kategori", "dist_stat", "dist_tj"]].copy()
        disp_df = disp_df.rename(columns={
            "name":      "Perguruan Tinggi",
            "status":    "Status",
            "akreditasi":"Akreditasi",
            "mahasiswa": "Mahasiswa",
            "kategori":  "Aksesibilitas",
            "dist_stat": "Jarak Stasiun (m)",
            "dist_tj":   "Jarak Halte TJ (m)"
        })
        disp_df["Jarak Stasiun (m)"] = disp_df["Jarak Stasiun (m)"].round(0).astype(int)
        disp_df["Jarak Halte TJ (m)"] = disp_df["Jarak Halte TJ (m)"].round(0).astype(int)
        disp_df = disp_df.sort_values("Jarak Stasiun (m)").reset_index(drop=True)
        st.dataframe(disp_df, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 2: SOAL 2 - SISTEM REKOMENDASI KAMPUS SATELIT (ML RANDOM FOREST)
# ==============================================================================
with tab2:
    st.markdown("""
        <div class='context-card'>
        <strong>Modul Soal 2:</strong> Sistem rekomendasi zonasi kelayakan lokasi pembangunan Kampus Satelit / Program Studi Baru berbasis algoritma
        <strong>Machine Learning Random Forest Classifier</strong>. Model mengklasifikasikan 299 kecamatan di wilayah Jabodetabek & Karawang ke dalam 3 zona:
        <strong>Sangat Direkomendasikan (Kelas 2)</strong>, <strong>Cukup Direkomendasikan (Kelas 1)</strong>, dan <strong>Tidak Direkomendasikan (Kelas 0)</strong>.
        Akurasi evaluasi model: <strong>85.00%</strong>.
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Filter Controls for Tab 2
    st.sidebar.markdown("<div class='sidebar-title'>Filter Tab 2: Rekomendasi ML</div>", unsafe_allow_html=True)
    all_kab = ["Semua Kabupaten/Kota"] + sorted(df_pred["KAB_KOTA"].dropna().unique().tolist())
    selected_kab = st.sidebar.selectbox("Kabupaten / Kota", all_kab, key="t2_kab")

    reko_options = ["Semua Tingkat", "Sangat Direkomendasikan (2)", "Cukup Direkomendasikan (1)", "Tidak Direkomendasikan (0)"]
    selected_reko = st.sidebar.selectbox("Tingkat Rekomendasi", reko_options, key="t2_reko")

    # Filter dataframe
    df_reko = df_pred.copy()
    if selected_kab != "Semua Kabupaten/Kota":
        df_reko = df_reko[df_reko["KAB_KOTA"] == selected_kab]

    if selected_reko.startswith("Sangat"):
        df_reko = df_reko[df_reko["Pred_Reko"] == 2]
    elif selected_reko.startswith("Cukup"):
        df_reko = df_reko[df_reko["Pred_Reko"] == 1]
    elif selected_reko.startswith("Tidak"):
        df_reko = df_reko[df_reko["Pred_Reko"] == 0]

    # Calculate Top Metrics for Tab 2
    tot_kec   = len(df_reko)
    cnt_sangat = len(df_reko[df_reko["Pred_Reko"] == 2])
    cnt_cukup  = len(df_reko[df_reko["Pred_Reko"] == 1])
    cnt_tidak  = len(df_reko[df_reko["Pred_Reko"] == 0])

    pct_sangat = (cnt_sangat / tot_kec * 100) if tot_kec > 0 else 0
    pct_cukup  = (cnt_cukup / tot_kec * 100) if tot_kec > 0 else 0
    pct_tidak  = (cnt_tidak / tot_kec * 100) if tot_kec > 0 else 0

    m2_1, m2_2, m2_3, m2_4 = st.columns(4)
    with m2_1:
        st.metric("Kecamatan Terfilter", f"{tot_kec}")
    with m2_2:
        st.metric("Sangat Direkomendasikan", f"{cnt_sangat} Kec.", delta=f"{pct_sangat:.1f}%")
    with m2_3:
        st.metric("Cukup Direkomendasikan", f"{cnt_cukup} Kec.", delta=f"{pct_cukup:.1f}%", delta_color="off")
    with m2_4:
        st.metric("Tidak Direkomendasikan", f"{cnt_tidak} Kec.", delta=f"{pct_tidak:.1f}%", delta_color="inverse")

    # Create Folium Choropleth Map for Tab 2
    m2 = folium.Map(location=[-6.25, 106.84], zoom_start=10, tiles="CartoDB positron", control_scale=True)

    # Color mapping for Pred_Reko
    def get_color_reko(pred):
        if pred == 2:
            return "#10B981"  # Hijau - Sangat Direkomendasikan
        elif pred == 1:
            return "#F59E0B"  # Kuning - Cukup Direkomendasikan
        return "#EF4444"      # Merah - Tidak Direkomendasikan

    if kec_data:
        # Pre-filter features if Kab/Kota or Reko filter is active
        valid_kode_set = set(df_reko["KODE_KEC"].astype(str).str.strip())
        
        filtered_features = []
        for feat in kec_data["features"]:
            k_code = str(feat["properties"].get("KODE_KEC", "")).strip()
            if k_code in valid_kode_set:
                filtered_features.append(feat)

        geojson_tab2 = {
            "type": "FeatureCollection",
            "features": filtered_features
        }

        folium.GeoJson(
            geojson_tab2,
            name="Zonasi Rekomendasi Kampus Satelit",
            style_function=lambda feat: {
                "fillColor": get_color_reko(feat["properties"].get("Pred_Reko", 0)),
                "color": "#1E293B",
                "weight": 1.2,
                "fillOpacity": 0.65
            },
            highlight_function=lambda feat: {
                "fillColor": "#2563EB",
                "color": "#FFFFFF",
                "weight": 2.2,
                "fillOpacity": 0.85
            },
            popup=folium.GeoJsonPopup(
                fields=["KECAMATAN", "KAB_KOTA", "Pred_Reko", "sma_grad", "dist_ind", "toll_pct", "camp_dens", "area_km2"],
                aliases=["Kecamatan:", "Kab/Kota:", "Kode Rekomendasi (2=Sangat, 1=Cukup, 0=Tidak):", "Lulusan SMA:", "Jarak Industri (m):", "Akses Tol (m/m2):", "Kepadatan Kampus (unit/km2):", "Luas Wilayah (km2):"],
                style="background-color: #1E293B; color: #F8FAFC; font-family: sans-serif; font-size: 12px; padding: 8px; border-radius: 4px;"
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=["KECAMATAN", "KAB_KOTA", "Pred_Reko"],
                aliases=["Kecamatan:", "Kab/Kota:", "Label Rekomendasi ML:"],
                style="background-color: #1E293B; color: #F8FAFC; font-family: sans-serif; font-size: 12px; padding: 6px; border-radius: 4px;"
            )
        ).add_to(m2)

    # Inject Legend Overlay for Tab 2
    _legend_html2 = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 25px;
        right: 10px;
        z-index: 1000;
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 14px;
        font-family: sans-serif;
        font-size: 12px;
        color: #F8FAFC;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        min-width: 210px;
    ">
        <div style="font-weight:700; font-size:12px; margin-bottom:8px; color:#F8FAFC;">Legenda Zonasi ML Random Forest</div>
        <div style="margin-bottom:6px;">
            <span style="display:inline-block;width:12px;height:12px;background-color:#10B981;border-radius:3px;margin-right:7px;vertical-align:middle;"></span>
            <strong>Sangat Direkomendasikan</strong> (Kelas 2)
        </div>
        <div style="margin-bottom:6px;">
            <span style="display:inline-block;width:12px;height:12px;background-color:#F59E0B;border-radius:3px;margin-right:7px;vertical-align:middle;"></span>
            <strong>Cukup Direkomendasikan</strong> (Kelas 1)
        </div>
        <div>
            <span style="display:inline-block;width:12px;height:12px;background-color:#EF4444;border-radius:3px;margin-right:7px;vertical-align:middle;"></span>
            <strong>Tidak Direkomendasikan</strong> (Kelas 0)
        </div>
    </div>
    {% endmacro %}
    """

    class _LegendOverlay2(MacroElement):
        def __init__(self):
            super().__init__()
            self._template = Template(_legend_html2)

    m2.get_root().add_child(_LegendOverlay2())
    st_folium(m2, use_container_width=True, height=560, returned_objects=[], key="map_tab2")

    # Feature Importance Visualization Section
    st.divider()
    st.markdown("### Visualisasi Feature Importance (Tingkat Pengaruh Variabel Model ML)")
    st.markdown("Grafik berikut menunjukkan kontribusi kontributif dari 5 fitur spasial hasil ekstraksi QGIS yang digunakan model Random Forest dalam menentukan zona kelayakan kampus satelit baru:")

    fi_data = pd.DataFrame({
        "Variabel Fitur": [
            "Jumlah Lulusan SMA (sma_grad)",
            "Jarak ke Industri Terdekat (dist_ind)",
            "Persentase Akses Tol (toll_pct)",
            "Luas Wilayah Kecamatan (area_km2)",
            "Kepadatan Kampus Eksisting (camp_dens)"
        ],
        "Tingkat Pengaruh (%)": [36.99, 31.10, 17.29, 10.52, 4.09]
    }).sort_values("Tingkat Pengaruh (%)", ascending=True)

    chart = alt.Chart(fi_data).mark_bar(color="#3B82F6", cornerRadiusEnd=4).encode(
        x=alt.X("Tingkat Pengaruh (%):Q", title="Tingkat Pengaruh (Feature Importance %)"),
        y=alt.Y("Variabel Fitur:N", sort="-x", title="Variabel Fitur Spasial"),
        tooltip=["Variabel Fitur", "Tingkat Pengaruh (%)"]
    ).properties(height=240, width="container")

    st.altair_chart(chart, use_container_width=True)

    st.markdown("""
        * **Temuan Utama:** Faktor **Jumlah Lulusan SMA (`sma_grad`)** mendominasi pengaruh klasifikasi sebesar **36.99%**, diikuti oleh **Jarak ke Kawasan Industri (`dist_ind`)** sebesar **31.10%**.
        Hal ini membuktikan bahwa pasokan calon mahasiswa (input demografis) dan kedekatan mitra industri (vokasi) merupakan dua pilar utama dalam penentuan lokasi kampus baru (total kontribusi > 68%).
    """)

    # Interactive ML Model Simulator Panel
    st.divider()
    st.markdown("### Simulator Prediksi Rekomendasi ML Real-Time")
    st.markdown("Gunakan panel simulator berikut untuk menguji inferensi model Random Forest secara langsung dengan memasukkan nilai variabel spasial hipotetis:")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_sma   = st.slider("Jumlah Lulusan SMA (orang):", min_value=100, max_value=15000, value=3500, step=100)
        sim_dist  = st.slider("Jarak ke Kawasan Industri Terdekat (meter):", min_value=50, max_value=50000, value=2500, step=100)
        sim_toll  = st.slider("Persentase Akses Jalan Tol (m/m2):", min_value=0.0, max_value=0.05, value=0.005, step=0.001, format="%.4f")
    with sim_col2:
        sim_area  = st.slider("Luas Wilayah Kecamatan (km2):", min_value=5.0, max_value=150.0, value=45.0, step=1.0)
        sim_dens  = st.slider("Kepadatan Kampus Eksisting (unit/km2):", min_value=0.0, max_value=1.5, value=0.05, step=0.01)

    # Run live model inference
    input_vector = np.array([[sim_dist, sim_dens, sim_toll, sim_sma, sim_area]])
    pred_class   = rf_model.predict(input_vector)[0]
    pred_proba   = rf_model.predict_proba(input_vector)[0]

    st.markdown("#### Hasil Inferensi Prediksi Model:")
    if pred_class == 2:
        st.markdown(f"""
            <div class='reko-card-green'>
                Hasil Prediksi Model: SANGAT DIREKOMENDASIKAN (Kelas 2)<br>
                Tingkat Keyakinan (Probabilitas): {pred_proba[2]*100:.1f}%<br>
                <em>Analisis: Wilayah ini memiliki pasokan calon mahasiswa tinggi dan berada dalam jangkauan strategis kawasan industri & akses jalan tol.</em>
            </div>
        """, unsafe_allow_html=True)
    elif pred_class == 1:
        st.markdown(f"""
            <div class='reko-card-yellow'>
                Hasil Prediksi Model: CUKUP DIREKOMENDASIKAN (Kelas 1)<br>
                Tingkat Keyakinan (Probabilitas): {pred_proba[1]*100:.1f}%<br>
                <em>Analisis: Wilayah ini memenuhi kriteria sedang dan membutuhkan penguatan aksesibilitas atau rute feeder industri.</em>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='reko-card-red'>
                Hasil Prediksi Model: TIDAK DIREKOMENDASIKAN (Kelas 0)<br>
                Tingkat Keyakinan (Probabilitas): {pred_proba[0]*100:.1f}%<br>
                <em>Analisis: Wilayah ini terisolasi dari kawasan industri, memiliki jumlah lulusan SMA rendah, atau memiliki kepadatan kampus eksisting yang jenuh.</em>
            </div>
        """, unsafe_allow_html=True)

    # Filtered Kecamatan Data Table for Tab 2
    st.divider()
    st.caption(f"Tabel Hasil Prediksi Kecamatan Terfilter ({tot_kec} Wilayah)")
    disp_reko_df = df_reko[["KECAMATAN", "KAB_KOTA", "Pred_Reko", "sma_grad", "dist_ind", "toll_pct", "camp_dens", "area_km2"]].copy()
    disp_reko_df["Pred_Reko_Text"] = disp_reko_df["Pred_Reko"].map({
        2: "Sangat Direkomendasikan",
        1: "Cukup Direkomendasikan",
        0: "Tidak Direkomendasikan"
    })
    disp_reko_df = disp_reko_df.rename(columns={
        "KECAMATAN": "Kecamatan",
        "KAB_KOTA": "Kabupaten/Kota",
        "Pred_Reko_Text": "Status Rekomendasi ML",
        "sma_grad": "Lulusan SMA",
        "dist_ind": "Jarak Industri (m)",
        "toll_pct": "Akses Tol (m/m2)",
        "camp_dens": "Kepadatan Kampus",
        "area_km2": "Luas Wilayah (km2)"
    })
    disp_reko_df = disp_reko_df[["Kecamatan", "Kabupaten/Kota", "Status Rekomendasi ML", "Lulusan SMA", "Jarak Industri (m)", "Akses Tol (m/m2)", "Kepadatan Kampus", "Luas Wilayah (km2)"]]
    disp_reko_df["Jarak Industri (m)"] = disp_reko_df["Jarak Industri (m)"].round(1)
    disp_reko_df = disp_reko_df.sort_values(["Status Rekomendasi ML", "Lulusan SMA"], ascending=[False, False]).reset_index(drop=True)
    st.dataframe(disp_reko_df, use_container_width=True, hide_index=True)


# Calculate total render latency in milliseconds
t_end = time.perf_counter()
latency_ms = (t_end - t_start) * 1000

# Server Render Latency Badge Footer
st.markdown(f"""
    <div class='latency-footer'>
        Waktu Render Server Streamlit: <strong>{latency_ms:.1f} ms</strong> | Ukuran GeoJSON Teroptimasi: <strong>0.88 MB</strong> | Dikembangkan untuk UAS SIG E-504
    </div>
""", unsafe_allow_html=True)
