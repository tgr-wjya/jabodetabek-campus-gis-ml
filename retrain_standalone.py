"""
retrain_standalone.py
---------------------
Full standalone replacement for the QGIS training pipeline.
Runs outside QGIS — no iface, no QgsProject needed.

Pipeline:
  1. Read Kecamatan_Jabodetabek.shp (UTM48S) for polygons + Label_Reko
  2. Read Sebaran_Kampus_Eksisting.shp (WGS84) — reproject to UTM48S
  3. Read Kawasan_Industri_Jabodetabek.shp (WGS84) — reproject to UTM48S
  4. Read Akses_Jalan_Tol.shp (WGS84) — reproject to UTM48S
  5. Calculate per-kecamatan features: dist_ind, camp_dens, toll_pct, sma_grad, area_km2
  6. Train RandomForestClassifier (same hyperparams as train_qgis.py)
  7. Write kecamatan_predictions_qgis.csv
  8. Patch Pred_Reko into Kecamatan_UTM48S.dbf
"""

import csv
import shutil
import struct
from pathlib import Path

import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import shape
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

DATA = Path("data_ready")

# ── CRS transformer: WGS84 → UTM Zone 48S ─────────────────────────────────────
# always_xy=True keeps lon/lat order consistent
to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32748", always_xy=True)


def wgs_to_utm(geom_shape):
    """Reproject a Shapely geometry from WGS84 to UTM48S."""
    from shapely.ops import transform
    return transform(lambda x, y: to_utm.transform(x, y), geom_shape)


# ── Readers ────────────────────────────────────────────────────────────────────
def read_shapes(path):
    """Return list of (shapely_geom, record_dict) from a shapefile."""
    sf = shapefile.Reader(str(path))
    field_names = [f[0] for f in sf.fields[1:]]
    result = []
    for sr in sf.shapeRecords():
        geom = shape(sr.shape.__geo_interface__)
        rec  = dict(zip(field_names, sr.record))
        result.append((geom, rec))
    return result


def main():
    # ── 1. Kecamatan (UTM48S — use as-is) ─────────────────────────────────────────
    print("Reading Kecamatan_Jabodetabek.shp (UTM48S)...")
    kec_data = read_shapes(DATA / "Kecamatan_Jabodetabek.shp")
    print(f"  {len(kec_data)} kecamatan loaded")

    # ── 2. Campus points (WGS84 → UTM48S) ─────────────────────────────────────────
    print("Reading + reprojecting Sebaran_Kampus_Eksisting.shp (WGS84 → UTM48S)...")
    kam_points = []
    for geom, _ in read_shapes(DATA / "Sebaran_Kampus_Eksisting.shp"):
        if not geom.is_empty:
            kam_points.append(wgs_to_utm(geom))
    print(f"  {len(kam_points)} campus points loaded")

    # ── 3. Industrial zones (WGS84 → UTM48S) ──────────────────────────────────────
    print("Reading + reprojecting Kawasan_Industri_Jabodetabek.shp (WGS84 → UTM48S)...")
    ind_centroids = []
    for geom, _ in read_shapes(DATA / "Kawasan_Industri_Jabodetabek.shp"):
        if not geom.is_empty:
            ind_centroids.append(wgs_to_utm(geom).centroid)
    print(f"  {len(ind_centroids)} industrial centroids loaded")

    # ── 4. Toll roads (WGS84 → UTM48S) ───────────────────────────────────────────
    print("Reading + reprojecting Akses_Jalan_Tol.shp (WGS84 → UTM48S)...")
    tol_lines = []
    for geom, _ in read_shapes(DATA / "Akses_Jalan_Tol.shp"):
        if not geom.is_empty:
            tol_lines.append(wgs_to_utm(geom))
    print(f"  {len(tol_lines)} toll segments loaded")

    # ── 5. Calculate features ──────────────────────────────────────────────────────
    print("\nCalculating spatial features per kecamatan...")

    X_rows   = []
    y_rows   = []
    metadata = []

    for i, (kec_geom, rec) in enumerate(kec_data):
        if kec_geom.is_empty:
            continue

        area_m2  = kec_geom.area
        area_km2 = area_m2 / 1_000_000.0

        # a. Distance to nearest industrial centroid (metres, UTM)
        min_dist = min((kec_geom.centroid.distance(c) for c in ind_centroids), default=0.0)

        # b. Campus density (count inside polygon / area_km2)
        n_camp = sum(1 for pt in kam_points if kec_geom.contains(pt))
        camp_dens = (n_camp / area_km2) if area_km2 > 0 else 0.0

        # c. Toll road coverage percentage inside polygon
        tol_len = sum(kec_geom.intersection(tl).length for tl in tol_lines if kec_geom.intersects(tl))
        poly_perim = kec_geom.length
        toll_pct = (tol_len / poly_perim * 100.0) if poly_perim > 0 else 0.0

        # d. High school graduate count (read directly from record)
        sma_grad = float(rec.get("sma_grad") or 0)

        # e. Target label
        label_reko = int(rec.get("Label_Reko") or 0)

        X_rows.append([min_dist, camp_dens, toll_pct, sma_grad, area_km2])
        y_rows.append(label_reko)
        metadata.append({
            "KODE_KEC":  str(rec.get("KODE_KEC", "")),
            "KECAMATAN": str(rec.get("KECAMATAN", "")),
            "KAB_KOTA":  str(rec.get("KAB_KOTA", "")),
            "PROVINSI":  str(rec.get("PROVINSI", "")),
        })

    X = np.array(X_rows, dtype=np.float64)
    y = np.array(y_rows, dtype=np.int64)

    print(f"Features matrix shape: {X.shape}")
    print(f"Class distribution: 0={sum(y==0)}, 1={sum(y==1)}, 2={sum(y==2)}")

    # ── 6. Train RandomForest (same parameters as train_qgis.py) ───────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy (Test Set): {acc:.4f} ({acc*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Feature Importance
    feats = ["dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2"]
    imps  = clf.feature_importances_
    print("\nFeature Importances:")
    for f_name, imp in sorted(zip(feats, imps), key=lambda t: t[1], reverse=True):
        print(f"  {f_name:12s}: {imp:.4f}")

    # Retrain on full dataset
    clf.fit(X, y)
    all_preds = clf.predict(X)

    # ── 7. Write kecamatan_predictions_qgis.csv ───────────────────────────────────
    csv_path = DATA / "kecamatan_predictions_qgis.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["KODE_KEC", "KECAMATAN", "KAB_KOTA", "PROVINSI",
                         "Label_Reko", "Pred_Reko"])
        for idx, row in enumerate(metadata):
            writer.writerow([
                row["KODE_KEC"], row["KECAMATAN"],
                row["KAB_KOTA"],  row["PROVINSI"],
                y[idx], all_preds[idx]
            ])
    print(f"Predictions written: {csv_path}")

    # ── 8. Patch Kecamatan_UTM48S.dbf ─────────────────────────────────────────────
    DBF    = DATA / "Kecamatan_UTM48S.dbf"
    BACKUP = DATA / "Kecamatan_UTM48S.dbf.bak2"
    shutil.copy(DBF, BACKUP)

    pred_map = {row["KODE_KEC"]: int(pred)
                for row, pred in zip(metadata, all_preds)}

    with open(DBF, "rb") as f:
        raw = f.read()

    n_records  = struct.unpack_from("<I", raw, 4)[0]
    header_end = struct.unpack_from("<H", raw, 8)[0]
    rec_size   = struct.unpack_from("<H", raw, 10)[0]

    fields, pos = [], 32
    while raw[pos] != 0x0D:
        name  = raw[pos:pos+11].rstrip(b"\x00").decode("ascii", errors="replace")
        flen  = raw[pos+16]
        fields.append({"name": name, "len": flen})
        pos  += 32

    offset = 1
    for fld in fields:
        fld["offset"] = offset
        offset += fld["len"]

    kode_fld = next(f for f in fields if f["name"] == "KODE_KEC")
    pred_fld = next(f for f in fields if f["name"] == "Pred_Reko")

    data    = bytearray(raw)
    updated = 0
    for i in range(n_records):
        rs   = header_end + i * rec_size
        kode = data[rs + kode_fld["offset"]:
                    rs + kode_fld["offset"] + kode_fld["len"]]
        kode_str = kode.decode("ascii", errors="replace").strip()
        if kode_str in pred_map:
            encoded = str(pred_map[kode_str]).rjust(pred_fld["len"]).encode("ascii")
            data[rs + pred_fld["offset"]:
                 rs + pred_fld["offset"] + pred_fld["len"]] = encoded
            updated += 1

    with open(DBF, "wb") as f:
        f.write(bytes(data))

    print(f"Kecamatan_UTM48S.dbf updated: {updated}/{n_records} records")
    print("Done.")


if __name__ == "__main__":
    main()
