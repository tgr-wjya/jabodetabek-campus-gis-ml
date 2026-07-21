# test_latency.py
import json
import time
import os

def benchmark_geojson(file_path):
    start_time = time.perf_counter()
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    load_duration_ms = (time.perf_counter() - start_time) * 1000
    feature_count = len(data.get("features", []))
    
    return {
        "file": os.path.basename(file_path),
        "size_mb": file_size_mb,
        "features": feature_count,
        "latency_ms": load_duration_ms
    }

def main():
    print("=" * 60)
    print("Pengujian Latensi & Ukuran GeoJSON Spasial")
    print("=" * 60)
    
    heavy_path = "data_ready/Kecamatan_Batas_Kecil.geojson"
    light_path = "data_ready/Kecamatan_ML_Simplified.geojson"
    
    res_heavy = benchmark_geojson(heavy_path)
    res_light = benchmark_geojson(light_path)
    
    print(f"Versi Asal    ({res_heavy['file']}): {res_heavy['size_mb']:.2f} MB | {res_heavy['features']} Fitur | {res_heavy['latency_ms']:.2f} ms")
    print(f"Versi Ringkas ({res_light['file']}): {res_light['size_mb']:.2f} MB | {res_light['features']} Fitur | {res_light['latency_ms']:.2f} ms")
    
    speedup = res_heavy['latency_ms'] / max(res_light['latency_ms'], 0.001)
    size_reduction = (1 - (res_light['size_mb'] / res_heavy['size_mb'])) * 100
    
    print("-" * 60)
    print(f"Pengurangan Ukuran Berkas     : {size_reduction:.2f}%")
    print(f"Peningkatan Kecepatan Latensi : {speedup:.2f}x lebih cepat")
    print("=" * 60)

if __name__ == "__main__":
    main()
