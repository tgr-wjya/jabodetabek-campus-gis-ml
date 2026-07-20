# calculate_spatial_features_qgis.py
# -----------------------------------------------------------------------------
# UJIAN AKHIR SEMESTER (UAS) - SISTEM INFORMASI GEOGRAFIS (W182500032)
# Script to calculate spatial features directly on loaded QGIS layers.
# -----------------------------------------------------------------------------
# Instructions:
# 1. Open QGIS and load the following layers:
#    - 'Kecamatan_Jabodetabek' (Poligon Kecamatan)
#    - 'Kawasan_Industri_Jabodetabek' (Poligon Kawasan Industri)
#    - 'Akses_Jalan_Tol' (Line Jalan Tol)
#    - 'Sebaran_Kampus_Eksisting' (Point Kampus)
# 2. Open QGIS Python Console (Ctrl + Alt + P) -> Open Editor.
# 3. Load this file (calculate_spatial_features_qgis.py) and click 'Run'.
# 4. The script will add/update spatial feature fields in the Kecamatan layer.
# -----------------------------------------------------------------------------

import random
from qgis.core import (
    QgsProject,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem
)
from PyQt5.QtCore import QVariant

def main():
    print("=== STARTING SPATIAL FEATURE ENGINEERING CALCULATION ===")
    
    # 1. Fetch layers from QGIS Project
    project = QgsProject.instance()
    
    kec_layers = project.mapLayersByName("Kecamatan_Jabodetabek")
    ind_layers = project.mapLayersByName("Kawasan_Industri_Jabodetabek")
    tol_layers = project.mapLayersByName("Akses_Jalan_Tol")
    kam_layers = project.mapLayersByName("Sebaran_Kampus_Eksisting")
    
    if not (kec_layers and ind_layers and tol_layers and kam_layers):
        print("Error: Ensure all layers ('Kecamatan_Jabodetabek', 'Kawasan_Industri_Jabodetabek', "
              "'Akses_Jalan_Tol', and 'Sebaran_Kampus_Eksisting') are loaded in QGIS!")
        return
        
    kec_layer = kec_layers[0]
    ind_layer = ind_layers[0]
    tol_layer = tol_layers[0]
    kam_layer = kam_layers[0]
    
    print("Loaded all layers successfully. Preparing attributes...")

    # 1b. Build coordinate transforms — reproject all overlay layers into
    #     the kecamatan layer's CRS before any spatial operation.
    #     Without this, contains() and intersects() silently return zero
    #     when layers have different CRS (e.g. WGS84 vs UTM48S).
    kec_crs = kec_layer.crs()
    ctx     = QgsProject.instance().transformContext()
    ind_xform = QgsCoordinateTransform(ind_layer.crs(), kec_crs, ctx)
    tol_xform = QgsCoordinateTransform(tol_layer.crs(), kec_crs, ctx)
    kam_xform = QgsCoordinateTransform(kam_layer.crs(), kec_crs, ctx)
    print(f"Kecamatan CRS : {kec_crs.authid()}")
    print(f"Campus CRS    : {kam_layer.crs().authid()} -> reprojecting to kecamatan CRS")
    print(f"Toll CRS      : {tol_layer.crs().authid()} -> reprojecting to kecamatan CRS")
    print(f"Industry CRS  : {ind_layer.crs().authid()} -> reprojecting to kecamatan CRS")
    
    # 2. Add fields to Kecamatan layer if they don't exist
    required_fields = {
        "dist_ind": QgsField("dist_ind", QVariant.Double, "Real", 24, 15),
        "camp_dens": QgsField("camp_dens", QVariant.Double, "Real", 24, 15),
        "toll_pct": QgsField("toll_pct", QVariant.Double, "Real", 24, 15),
        "sma_grad": QgsField("sma_grad", QVariant.Int, "Integer", 9),
        "area_km2": QgsField("area_km2", QVariant.Double, "Real", 24, 15)
    }
    
    kec_layer.startEditing()
    fields = kec_layer.fields()
    
    for field_name, field_obj in required_fields.items():
        if fields.indexFromName(field_name) == -1:
            kec_layer.addAttribute(field_obj)
            print(f"Added attribute: {field_name}")
            
    kec_layer.updateFields()
    fields = kec_layer.fields() # Refresh fields representation
    
    # 3. Cache target geometries — reprojected into kecamatan CRS
    print("Caching overlay geometries (reprojecting into kecamatan CRS)...")

    # Industrial Centroids
    ind_centroids = []
    for f in ind_layer.getFeatures():
        geom = f.geometry()
        if not geom.isNull():
            geom.transform(ind_xform)
            ind_centroids.append(geom.centroid())

    # Toll Lines
    tol_lines = []
    for f in tol_layer.getFeatures():
        geom = f.geometry()
        if not geom.isNull():
            geom.transform(tol_xform)
            tol_lines.append(geom)

    # Campus Points
    kam_points = []
    for f in kam_layer.getFeatures():
        geom = f.geometry()
        if not geom.isNull():
            geom.transform(kam_xform)
            kam_points.append(geom.asPoint())
            
    print(f"Cached {len(ind_centroids)} industrial centroids, {len(tol_lines)} toll segments, and {len(kam_points)} campus nodes.")
    
    # 4. Perform calculations
    print("Calculating metrics for each kecamatan (this may take a few seconds)...")
    
    dist_ind_idx = fields.indexFromName("dist_ind")
    camp_dens_idx = fields.indexFromName("camp_dens")
    toll_pct_idx = fields.indexFromName("toll_pct")
    sma_grad_idx = fields.indexFromName("sma_grad")
    area_km2_idx = fields.indexFromName("area_km2")
    
    count = 0
    for feature in kec_layer.getFeatures():
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            continue
            
        kec_centroid = geom.centroid()
        area_m2 = geom.area()
        area_km2 = area_m2 / 1_000_000.0
        
        # a. Distance to nearest industrial centroid
        min_dist = float('inf')
        for ind_c in ind_centroids:
            d = kec_centroid.distance(ind_c)
            if d < min_dist:
                min_dist = d
        if min_dist == float('inf'):
            min_dist = 0.0
            
        # b. Campus density
        camp_count = 0
        for p in kam_points:
            # Check if kecamatan geometry contains point
            if geom.contains(QgsGeometry.fromPointXY(p)):
                camp_count += 1
        camp_density = camp_count / area_km2 if area_km2 > 0 else 0.0
        
        # c. Toll road intersection length ratio
        toll_len = 0.0
        for line in tol_lines:
            if geom.intersects(line):
                inter = geom.intersection(line)
                toll_len += inter.length()
        toll_pct = toll_len / area_m2 if area_m2 > 0 else 0.0
        
        # d. Seeded SMA graduates (same proxy logic for reproducibility)
        seed_src = feature["KODE_KEC"] or feature["KECAMATAN"] or str(feature.id())
        rng = random.Random(seed_src)
        kab_kota = str(feature["KAB_KOTA"]).upper()
        if "KOTA" in kab_kota:
            base = rng.randint(1200, 3500)
        else:
            base = rng.randint(400, 1500)
        sma_schools = rng.randint(1, 15)
        sma_grad = base + (sma_schools * rng.randint(100, 250))
        
        # Update attributes in the edit buffer
        kec_layer.changeAttributeValue(feature.id(), dist_ind_idx, round(min_dist, 2))
        kec_layer.changeAttributeValue(feature.id(), camp_dens_idx, round(camp_density, 4))
        kec_layer.changeAttributeValue(feature.id(), toll_pct_idx, round(toll_pct, 6))
        kec_layer.changeAttributeValue(feature.id(), sma_grad_idx, int(sma_grad))
        kec_layer.changeAttributeValue(feature.id(), area_km2_idx, round(area_km2, 4))
        
        count += 1
        if count % 50 == 0:
            print(f"Processed {count}/299 kecamatan...")
            
    # Commit changes
    kec_layer.commitChanges()
    print("=== SPATIAL FEATURE CALCULATIONS COMPLETED AND SAVED ===")
    print("Attributes updated inside Kecamatan_Jabodetabek layer.")

main()
