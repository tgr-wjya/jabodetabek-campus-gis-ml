# test_simplify_data.py
import json
import os
import unittest


class TestSimplifyData(unittest.TestCase):
    def test_simplified_geojson_exists_and_valid(self):
        output_path = "data_ready/Kecamatan_ML_Simplified.geojson"
        self.assertTrue(os.path.exists(output_path), "File Kecamatan_ML_Simplified.geojson harus ada")
        
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        self.assertLess(file_size_mb, 1.2, f"Ukuran file harus di bawah 1.2 MB, terdeteksi {file_size_mb:.2f} MB")
        
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 200)
        
        first_props = data["features"][0]["properties"]
        required_keys = ["KODE_KEC", "KECAMATAN", "KAB_KOTA", "dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2", "Pred_Reko"]
        for key in required_keys:
            self.assertIn(key, first_props, f"Properti '{key}' tidak ditemukan pada fitur GeoJSON")

if __name__ == "__main__":
    unittest.main()
