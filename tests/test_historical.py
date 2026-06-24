from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_historical_replay():
    response = client.post("/historical-replay", json={"scenario_name": "2008 Financial Crisis"})
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "simulated" in data
    # 2008 should cause severe GDP drop
    assert data["simulated"]["gdp"] < -0.01
