#!/usr/bin/env python3
"""
Geocodes TMU and RPTRA datasets from Jakarta Satu Data for the GIS UAS project.

TMU has a real `alamat` field -> geocoded directly.
RPTRA has no address -> geocoded from nama_rptra + kelurahan + kecamatan + "Jakarta",
which is unreliable (generic names like "Mawar", "Anggrek" collide with unrelated
places). Every RPTRA result gets a confidence flag - review anything not "high"
on a map before trusting it.

Usage:
    python geocode_tmu_rptra.py

Output:
    tmu_geocoded.csv
    rptra_geocoded.csv
    geocode_cache.json   (resume-safe cache, safe to delete to force re-geocode)
"""

import json
import time
import csv
import os
import sys
from urllib.parse import quote

import requests

TMU_URL = "https://ws.jakarta.go.id/gateway/DataPortalSatuDataJakarta/1.0/satudata?kategori=dataset&tipe=detail&url=data-tempat-pemakaman-umum-tpu"
RPTRA_URL = "https://ws.jakarta.go.id/gateway/DataPortalSatuDataJakarta/1.0/satudata?kategori=dataset&tipe=detail&url=jumlah-ruang-publik-terpadu-ramah-anak-rptra"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Nominatim's usage policy requires a real identifying User-Agent and a
# hard 1 req/sec cap. Don't parallelize this without switching providers.
HEADERS = {"User-Agent": "UAS-SIG-geocoder/1.0 (student project, contact: tgrwjya6371+services@gmail.com)"}
RATE_LIMIT_SECONDS = 1.1

CACHE_PATH = "geocode_cache.json"


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def fetch_json(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["data"]


def dedupe(rows, key_fn):
    """Keep the first occurrence per key. periode_data repeats (2023/2024/2025)
    for the same physical place, so raw rows massively overcount locations."""
    seen = {}
    for row in rows:
        k = key_fn(row)
        if k not in seen:
            seen[k] = row
    return list(seen.values())


def geocode_query(query, cache):
    """Single Nominatim lookup with caching + rate limiting. Returns the raw
    top result dict or None."""
    if query in cache:
        return cache[query]

    params = {"q": query, "format": "jsonv2", "limit": 1, "countrycodes": "id"}
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    results = resp.json()
    result = results[0] if results else None
    cache[query] = result
    time.sleep(RATE_LIMIT_SECONDS)
    return result


def geocode_tmu(rows, cache):
    out = []
    total = len(rows)
    for i, row in enumerate(rows, 1):
        query = row["alamat"]
        print(f"[TMU {i}/{total}] {row['nama_tpu']}", file=sys.stderr)
        try:
            result = geocode_query(query, cache)
        except requests.RequestException as e:
            print(f"  request failed: {e}", file=sys.stderr)
            result = None

        if result:
            lat, lon = result["lat"], result["lon"]
            # importance is Nominatim's own relevance score (0-1ish); "type"
            # tells you what kind of feature actually matched.
            confidence = "high" if float(result.get("importance", 0)) > 0.3 else "medium"
            match_type = result.get("type", "")
        else:
            lat = lon = ""
            confidence = "FAILED"
            match_type = ""

        out.append({
            "nama_tpu": row["nama_tpu"],
            "wilayah": row["wilayah"],
            "kecamatan": row["kecamatan"],
            "kelurahan": row["kelurahan"],
            "alamat": row["alamat"],
            "luas": row.get("luas", ""),
            "unit_agama": row.get("unit_agama", ""),
            "jumlah_terisi": row.get("jumlah_terisi", ""),
            "lat": lat,
            "lon": lon,
            "confidence": confidence,
            "nominatim_match_type": match_type,
        })
    return out


def geocode_rptra(rows, cache):
    out = []
    total = len(rows)
    for i, row in enumerate(rows, 1):
        # No address field exists. This query is a best-effort guess and
        # WILL false-positive on generic names (Mawar, Anggrek, Beringin...).
        query = f"RPTRA {row['nama_rptra']}, {row['kelurahan']}, {row['kecamatan']}, Jakarta, Indonesia"
        print(f"[RPTRA {i}/{total}] {row['nama_rptra']}", file=sys.stderr)
        try:
            result = geocode_query(query, cache)
        except requests.RequestException as e:
            print(f"  request failed: {e}", file=sys.stderr)
            result = None

        if not result:
            # Fallback: drop the specific name, just anchor to the kelurahan
            # centroid. Coarse, but better than nothing and clearly flagged.
            fallback_query = f"{row['kelurahan']}, {row['kecamatan']}, Jakarta, Indonesia"
            try:
                result = geocode_query(fallback_query, cache)
                fallback_used = True
            except requests.RequestException:
                result = None
                fallback_used = False
        else:
            fallback_used = False

        if result:
            lat, lon = result["lat"], result["lon"]
            display_name = result.get("display_name", "")
            # RPTRA queries are inherently low-trust: cap confidence at
            # "medium" even on a clean Nominatim hit, and mark fallbacks low.
            if fallback_used:
                confidence = "LOW - kelurahan centroid only, not the actual park"
            elif row["nama_rptra"].lower() in display_name.lower():
                confidence = "medium - name matched in result"
            else:
                confidence = "LOW - name not found in matched address, verify manually"
        else:
            lat = lon = ""
            display_name = ""
            confidence = "FAILED"

        out.append({
            "nama_rptra": row["nama_rptra"],
            "wilayah": row["wilayah"],
            "kecamatan": row["kecamatan"],
            "kelurahan": row["kelurahan"],
            "lat": lat,
            "lon": lon,
            "confidence": confidence,
            "nominatim_display_name": display_name,
        })
    return out


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    cache = load_cache()

    print("Fetching TMU dataset...", file=sys.stderr)
    tmu_raw = fetch_json(TMU_URL)
    tmu_unique = dedupe(tmu_raw, lambda r: (r["nama_tpu"], r["alamat"]))
    print(f"TMU: {len(tmu_raw)} rows -> {len(tmu_unique)} unique locations", file=sys.stderr)

    print("Fetching RPTRA dataset...", file=sys.stderr)
    rptra_raw = fetch_json(RPTRA_URL)
    rptra_unique = dedupe(rptra_raw, lambda r: (r["nama_rptra"], r["kelurahan"], r["kecamatan"]))
    print(f"RPTRA: {len(rptra_raw)} rows -> {len(rptra_unique)} unique locations", file=sys.stderr)

    try:
        tmu_out = geocode_tmu(tmu_unique, cache)
    finally:
        save_cache(cache)  # save progress even if it crashes mid-run

    try:
        rptra_out = geocode_rptra(rptra_unique, cache)
    finally:
        save_cache(cache)

    write_csv(
        "tmu_geocoded.csv", tmu_out,
        ["nama_tpu", "wilayah", "kecamatan", "kelurahan", "alamat", "luas",
         "unit_agama", "jumlah_terisi", "lat", "lon", "confidence", "nominatim_match_type"],
    )
    write_csv(
        "rptra_geocoded.csv", rptra_out,
        ["nama_rptra", "wilayah", "kecamatan", "kelurahan", "lat", "lon",
         "confidence", "nominatim_display_name"],
    )

    tmu_failed = sum(1 for r in tmu_out if r["confidence"] == "FAILED")
    rptra_low = sum(1 for r in rptra_out if "LOW" in r["confidence"] or r["confidence"] == "FAILED")
    print(f"\nDone. TMU failed geocodes: {tmu_failed}/{len(tmu_out)}", file=sys.stderr)
    print(f"RPTRA low-confidence/failed: {rptra_low}/{len(rptra_out)} -- review these manually before using", file=sys.stderr)


if __name__ == "__main__":
    main()
