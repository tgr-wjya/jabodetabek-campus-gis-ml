# simplify_data.py
import json
import os

import pandas as pd
from shapely.geometry import mapping, shape


def round_coords(coords):
    if isinstance(coords, (list, tuple)):
        if len(coords) >= 2 and isinstance(coords[0], (int, float)):
            return [round(coords[0], 5), round(coords[1], 5)]
        return [round_coords(c) for c in coords]
    return coords

def simplify_and_prejoin():
    input_geojson = "data_ready/Kecamatan_Batas_Kecil.geojson"
    input_csv = "data_ready/kecamatan_predictions.csv"
    output_geojson = "data_ready/Kecamatan_ML_Simplified.geojson"

    print("Memuat CSV hasil prediksi Machine Learning...")
    df_pred = pd.read_csv(input_csv)
    df_pred["KODE_KEC"] = df_pred["KODE_KEC"].astype(str).str.strip()
    pred_dict = df_pred.set_index("KODE_KEC").to_dict(orient="index")

    print("Memuat berkas GeoJSON utama...")
    with open(input_geojson, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    print("Menyederhanakan geometri poligon kecamatan dan menggabungkan properti ML...")
    features = []
    for feat in geojson_data["features"]:
        orig_props = feat["properties"]
        kode_kec = str(orig_props.get("KODE_KEC", "")).strip()
        
        # Simplify geometry using Shapely
        geom_shape = shape(feat["geometry"])
        simplified_geom = geom_shape.simplify(tolerance=0.0004, preserve_topology=True)
        raw_geom = mapping(simplified_geom)
        
        # Round coordinates to 5 decimal places (~1m precision)
        raw_geom["coordinates"] = round_coords(raw_geom["coordinates"])
        
        props = {
            "KODE_KEC": kode_kec,
            "KECAMATAN": str(orig_props.get("KECAMATAN", "")),
            "KAB_KOTA": str(orig_props.get("KAB_KOTA", "")),
            "dist_ind": float(orig_props.get("dist_ind", 0.0)),
            "camp_dens": float(orig_props.get("camp_dens", 0.0)),
            "toll_pct": float(orig_props.get("toll_pct", 0.0)),
            "sma_grad": int(float(orig_props.get("sma_grad", 0))),
            "area_km2": float(orig_props.get("area_km2", 0.0)),
            "Pred_Reko": int(float(orig_props.get("Pred_Reko", 0)))
        }

        if kode_kec in pred_dict:
            cdata = pred_dict[kode_kec]
            props["dist_ind"] = float(cdata.get("dist_ind", props["dist_ind"]))
            props["camp_dens"] = float(cdata.get("camp_dens", props["camp_dens"]))
            props["toll_pct"] = float(cdata.get("toll_pct", props["toll_pct"]))
            props["sma_grad"] = int(float(cdata.get("sma_grad", props["sma_grad"])))
            props["area_km2"] = float(cdata.get("area_km2", props["area_km2"]))
            props["Pred_Reko"] = int(float(cdata.get("Pred_Reko", props["Pred_Reko"])))

        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": raw_geom
        })

    out_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    print(f"Menulis berkas GeoJSON teroptimasi ke {output_geojson}...")
    with open(output_geojson, "w", encoding="utf-8") as f:
        json.dump(out_collection, f, separators=(',', ':'))

    size_mb = os.path.getsize(output_geojson) / (1024 * 1024)
    print(f"Berhasil membuat {output_geojson} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    simplify_and_prejoin()


