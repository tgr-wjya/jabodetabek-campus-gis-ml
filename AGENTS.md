# Project Agent Instructions

Project-specific guidelines for **Jabodetabek Campus GIS & Machine Learning WebApp**.

## 1. Architecture & Domain Logic
- **Streamlit Web App**: `app.py` serves the interactive WebGIS interface with Folium maps.
- **ML Suitability Pipeline**: Random Forest Classifier predicting sub-district recommendation levels (Class 0: Not Recommended, Class 1: Moderately Recommended, Class 2: Highly Recommended) using 5 features (`sma_grad`, `dist_ind`, `toll_pct`, `area_km2`, `camp_dens`).
- **Spatial Optimization**: Sub-district boundary GeoJSONs in `data_ready/` are simplified via Douglas-Peucker (`simplify_data.py`, `tolerance=0.0004`) to maintain file size < 1 MB and rendering latency < 20 ms.
- **Desktop QGIS vs Standalone**: QGIS Desktop GUI scripts (`train_qgis.py`, `calculate_spatial_features_qgis.py`) rely on embedded `iface` globals and `qgis.core`. Standalone Python execution uses `retrain_standalone.py`.

## 2. Command & Tooling Rules
- **RTK Command Prefix**: Always prefix shell commands with `rtk` (e.g. `rtk .venv/bin/ruff check .`, `rtk .venv/bin/pytest`).
- **Zero-Emoji Rule**: Under no circumstances generate emojis in code, comments, console logs, documentation, artifacts, or responses.
- **Context7 Docs**: Use Context7 CLI (`rtk npx ctx7@latest library <name> "<question>"`) for library/framework documentation lookups.

## 3. Verification & Quality Gates
- **Linting**: Run `rtk .venv/bin/ruff check .` to verify zero errors before committing.
- **Unit Testing**: Run `rtk .venv/bin/pytest --cov=. test_*.py` to verify test suite passes.
- **SonarCloud**: Configured in `sonar-project.properties` under organization `tgr-wjya-1` and project key `tgr-wjya-1_jabodetabek-campus-gis-ml`. Exclude non-unit-testable GUI/script files (`train_qgis.py`, `calculate_spatial_features_qgis.py`, `app.py`, `build_laporan_docx.py`) from coverage calculations.
- **Lighthouse CI**: Configured in `.lighthouserc.json`. Runs against `http://localhost:8501`. Performance threshold set to `warn`.

## 4. Git & Workspace Constraints
- **Excluded Assets**: Keep `screenshot/`, `.coverage`, `coverage.xml`, and `*.zip` in `.gitignore`. Do not commit screenshots.
- **Git Push Protocol**:
  1. Confirm `user.name` (`Tegar Wijaya Kusuma`) and `user.email` (`64220909+tgr-wjya@users.noreply.github.com`).
  2. Use `GIT_SSH_PASSPHRASE` from `.env` to unlock SSH keys.
  3. Explicitly inform the user beforehand prior to executing commit/push commands.
  4. Verify remote commit hash post-push via `git log origin/main -n 1`.

