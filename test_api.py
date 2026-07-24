from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_predict():
    payload = {
        "dist_ind": 3000.0,
        "camp_dens": 0.05,
        "toll_pct": 5.0,
        "sma_grad": 1500.0,
        "area_km2": 25.0
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probabilities" in data
    assert data["prediction"] in [0, 1, 2]
