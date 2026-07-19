# train_qgis.py
# -----------------------------------------------------------------------------
# UJIAN AKHIR SEMESTER (UAS) - SISTEM INFORMASI GEOGRAFIS (W182500032)
# Script to run Random Forest Classifier directly in QGIS Python Console.
# -----------------------------------------------------------------------------
# Instructions:
# 1. Open QGIS and load the 'Kecamatan_Jabodetabek' shapefile.
# 2. Select the 'Kecamatan_Jabodetabek' layer in the Layers panel so it is active.
# 3. Open QGIS Python Console (Ctrl + Alt + P or Plugins -> Python Console).
# 4. Click the 'Show Editor' button (the notepad icon in the console toolbar).
# 5. Open this file (train_qgis.py) in the QGIS Editor.
# 6. Click the green 'Run Script' play button.
# -----------------------------------------------------------------------------

import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 1. Access active layer in QGIS
layer = iface.activeLayer()

if not layer or layer.name() not in ["Kecamatan_Jabodetabek", "Kecamatan_Jabodetabek_Karawang"]:
    print("Warning: Please select the 'Kecamatan_Jabodetabek' layer in your Layers panel first!")
else:
    print(f"Active Layer Verified: {layer.name()}")
    
    # 2. Extract features and labels from layer attributes
    feature_names = ["dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2"]
    
    X_rows = []
    y_rows = []
    metadata = []
    
    for feature in layer.getFeatures():
        # Store metadata for CSV output
        metadata.append({
            "KODE_KEC": feature["KODE_KEC"],
            "KECAMATAN": feature["KECAMATAN"],
            "KAB_KOTA": feature["KAB_KOTA"],
            "PROVINSI": feature["PROVINSI"]
        })
        
        # Store features
        X_rows.append([
            float(feature["dist_ind"]),
            float(feature["camp_dens"]),
            float(feature["toll_pct"]),
            float(feature["sma_grad"]),
            float(feature["area_km2"])
        ])
        
        # Store target label (Label_Reko is stored as integer in shapefile)
        y_rows.append(int(feature["Label_Reko"]))
        
    X = np.array(X_rows)
    y = np.array(y_rows)
    
    print(f"Successfully loaded {X.shape[0]} kecamatan records.")
    
    # 3. Split dataset into train (80%) and test (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Train RandomForestClassifier
    print("Training Random Forest Classifier (100 estimators)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
    model.fit(X_train, y_train)
    
    # 5. Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("\n" + "="*40)
    print(f"Model Evaluation Accuracy: {accuracy:.4f}")
    print("="*40)
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["0 (Tidak)", "1 (Cukup)", "2 (Sangat)"]))
    
    # 6. Extract Feature Importance
    importances = model.feature_importances_
    print("\nFeature Importance:")
    print("-" * 30)
    for name, imp in zip(feature_names, importances):
        print(f"  {name:<10} : {imp:.4f} ({imp*100:.1f}%)")
    print("-" * 30)
    
    # Determine the most influential factor
    most_important_idx = np.argmax(importances)
    most_important_feature = feature_names[most_important_idx]
    most_important_val = importances[most_important_idx]
    print(f"Conclusion: The most determining factor for location suitability is '{most_important_feature}' ({most_important_val*100:.1f}% importance).\n")

    # 7. Optional: Predict for all records and write back to a local QGIS-compatible CSV
    all_preds = model.predict(X)
    
    # Identify layer directory to save predictions in the same place
    import os
    provider = layer.dataProvider()
    layer_source = provider.dataSourceUri()
    layer_dir = os.path.dirname(layer_source.split("|")[0])
    
    csv_output_path = os.path.join(layer_dir, "kecamatan_predictions_qgis.csv")
    
    print(f"Writing predictions to CSV: {csv_output_path}")
    try:
        with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["KODE_KEC", "KECAMATAN", "KAB_KOTA", "PROVINSI", "Label_Reko", "Pred_Reko"])
            for idx, row in enumerate(metadata):
                writer.writerow([
                    row["KODE_KEC"],
                    row["KECAMATAN"],
                    row["KAB_KOTA"],
                    row["PROVINSI"],
                    y[idx],
                    all_preds[idx]
                ])
        print("Success! CSV file created and ready for QGIS Join operation.")
    except Exception as e:
        print(f"Failed to write CSV: {e}")
