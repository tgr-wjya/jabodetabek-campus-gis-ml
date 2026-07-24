[![CI/CD Pipeline](https://github.com/tgr-wjya/jabodetabek-campus-gis-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/tgr-wjya/jabodetabek-campus-gis-ml/actions/workflows/ci.yml)

# WebGIS & Random Forest Campus Suitability

Streamlit WebGIS app for mapping transit accessibility of universities and recommending satellite campus locations in Jabodetabek and Karawang using a Random Forest model.

Live app: [https://jabodetabek-campus-gis-ml.streamlit.app/](https://jabodetabek-campus-gis-ml.streamlit.app/)

## Application Overview (`app.py`)

The Streamlit app consists of two tabs:

1. **Tab 1: Transit Accessibility Map**
   - Maps 266 universities in Jabodetabek & Karawang.
   - Classifies universities into:
     - **Transit-Oriented**: Within 1,000 m of a train station (KRL/MRT/LRT) or 500 m of a TransJakarta bus stop.
     - **Transit-Isolated**: Outside both coverage radiuses.
   - Displays train station points, bus stop points, and 1,000 m buffer zones.

2. **Tab 2: Random Forest Recommendation Map**
   - Displays a choropleth map of 299 sub-districts (*kecamatan*) divided into 3 recommendation levels:
     - **Class 2 (Green)**: Highly Recommended
     - **Class 1 (Yellow)**: Moderately Recommended
     - **Class 0 (Red)**: Not Recommended
   - Predicts suitability based on 5 features:
     1. High school graduate count (`sma_grad`)
     2. Distance to nearest industrial zone (`dist_ind`)
     3. Toll road coverage percentage (`toll_pct`)
     4. Sub-district land area (`area_km2`)
     5. Existing campus density (`camp_dens`)
   - Includes an interactive predictor simulator for testing input values against the trained model.

## Data Optimization (`simplify_data.py`)

- `simplify_data.py` uses the Douglas-Peucker algorithm (`tolerance=0.0004`) to simplify sub-district boundary polygons and pre-joins ML predictions.
- Reduces GeoJSON size from **17.44 MB to 0.88 MB** (94.98% smaller).
- Reduces rendering latency from **351.18 ms to 14.16 ms** per render.

## Project Structure

```
.
├── Project/
│   └── UAS.qgz                        # QGIS project file
├── data_ready/
│   ├── Kecamatan_ML_Simplified.geojson # Simplified sub-district boundaries with ML predictions
│   ├── Kecamatan_Batas_Kecil.geojson  # Original sub-district boundary GeoJSON
│   ├── Campuses_WebGIS.geojson        # University locations GeoJSON
│   ├── Stations_WebGIS.geojson        # Train stations GeoJSON
│   ├── Halte_TransJakarta.geojson     # TransJakarta bus stops GeoJSON
│   └── kecamatan_predictions.csv      # Model prediction CSV
├── app.py                             # Main Streamlit web application
├── simplify_data.py                   # Polygon simplification script
├── test_latency.py                    # Rendering latency benchmark script
├── test_simplify_data.py              # Tests for GeoJSON simplification
├── test_app_syntax.py                 # Tests for app.py compilation
├── calculate_spatial_features_qgis.py # QGIS feature extraction script
├── train_qgis.py                      # QGIS model training script
├── retrain_standalone.py              # Standalone model training script
├── requirements.txt                   # Python package dependencies
└── README.md                          # Repository documentation
```

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
