# generate_visualizations.py
import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape

def create_visualizations():
    os.makedirs("screenshot/visualizations", exist_ok=True)
    
    # --------------------------------------------------------------------------
    # 1. Feature Importance Chart (Grafik Feature Importance RF)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    features = [
        "Jumlah Lulusan SMA (sma_grad)",
        "Jarak ke Industri Terdekat (dist_ind)",
        "Persentase Akses Jalan Tol (toll_pct)",
        "Luas Wilayah Kecamatan (area_km2)",
        "Kepadatan Kampus Eksisting (camp_dens)"
    ]
    importances = [36.99, 31.10, 17.29, 10.52, 4.09]
    colors = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    
    y_pos = np.arange(len(features))
    bars = ax.barh(y_pos, importances, color=colors, height=0.6)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=10, fontweight='bold')
    ax.invert_yaxis()  # top-down order
    ax.set_xlabel("Tingkat Pengaruh (Feature Importance %)", fontsize=11, fontweight='bold')
    ax.set_title("Visualisasi Tingkat Pengaruh Variabel Spasial Model Random Forest (Soal 2)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlim(0, 45)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{width:.2f}%",
                va='center', ha='left', fontsize=10, fontweight='bold', color="#1E293B")
                
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    chart1_path = "screenshot/visualizations/Grafik_Feature_Importance_RF.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Berhasil membuat: {chart1_path}")

    # --------------------------------------------------------------------------
    # 2. Regional Breakdown Bar Chart (Grafik Distribusi Zonasi Kab/Kota)
    # --------------------------------------------------------------------------
    df_pred = pd.read_csv("data_ready/kecamatan_predictions.csv")
    
    # Group by Kab/Kota and Pred_Reko
    grouped = df_pred.groupby(["KAB_KOTA", "Pred_Reko"]).size().unstack(fill_value=0)
    grouped = grouped.rename(columns={
        2: "Sangat Direkomendasikan",
        1: "Cukup Direkomendasikan",
        0: "Tidak Direkomendasikan"
    })
    
    # Ensure all columns exist
    for col in ["Sangat Direkomendasikan", "Cukup Direkomendasikan", "Tidak Direkomendasikan"]:
        if col not in grouped.columns:
            grouped[col] = 0
            
    grouped["Total"] = grouped.sum(axis=1)
    grouped = grouped.sort_values("Total", ascending=True)
    grouped = grouped.drop(columns=["Total"])
    
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    colors_dict = {
        "Sangat Direkomendasikan": "#10B981",
        "Cukup Direkomendasikan": "#F59E0B",
        "Tidak Direkomendasikan": "#EF4444"
    }
    
    grouped.plot(kind="barh", stacked=True, ax=ax, color=[colors_dict[c] for c in grouped.columns], width=0.7)
    
    ax.set_title("Distribusi Zonasi Rekomendasi Kampus Satelit per Kabupaten/Kota (Jabodetabek & Karawang)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Jumlah Kecamatan", fontsize=11, fontweight='bold')
    ax.set_ylabel("Kabupaten / Kota", fontsize=11, fontweight='bold')
    ax.legend(title="Tingkat Rekomendasi ML", frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    chart2_path = "screenshot/visualizations/Grafik_Distribusi_Zonasi_KabKota.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Berhasil membuat: {chart2_path}")

    # --------------------------------------------------------------------------
    # 3. Spatial Choropleth Map Visualization (Peta Zonasi Rekomendasi ML)
    # --------------------------------------------------------------------------
    with open("data_ready/Kecamatan_ML_Simplified.geojson", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    
    reko_colors = {
        2: "#10B981",  # Hijau
        1: "#F59E0B",  # Kuning
        0: "#EF4444"   # Merah
    }
    
    for feat in data["features"]:
        geom = shape(feat["geometry"])
        pred = feat["properties"].get("Pred_Reko", 0)
        c = reko_colors.get(pred, "#EF4444")
        
        if geom.geom_type == 'Polygon':
            x, y = geom.exterior.xy
            ax.fill(x, y, alpha=0.8, fc=c, ec='#334155', linewidth=0.3)
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                ax.fill(x, y, alpha=0.8, fc=c, ec='#334155', linewidth=0.3)
                
    ax.set_title("PETA ZONASI REKOMENDASI LOKASI KAMPUS SATELIT / PRODI BARU (SOAL 2)\nModel Machine Learning Random Forest — Wilayah Jabodetabek & Karawang", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Bujur / Longitude (UTM/WGS84)", fontsize=10)
    ax.set_ylabel("Lintang / Latitude (UTM/WGS84)", fontsize=10)
    ax.set_facecolor('#F8FAFC')
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Custom Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#10B981', edgecolor='#334155', label='Kelas 2: Sangat Direkomendasikan (68 Kec)'),
        Patch(facecolor='#F59E0B', edgecolor='#334155', label='Kelas 1: Cukup Direkomendasikan (124 Kec)'),
        Patch(facecolor='#EF4444', edgecolor='#334155', label='Kelas 0: Tidak Direkomendasikan (107 Kec)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', title="Legenda Zonasi ML", frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=9)
    
    plt.tight_layout()
    chart3_path = "screenshot/visualizations/Peta_Zonasi_Rekomendasi_ML_Soal2.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Berhasil membuat: {chart3_path}")

if __name__ == "__main__":
    create_visualizations()
