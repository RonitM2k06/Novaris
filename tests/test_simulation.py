from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_simulate_endpoint():
    response = client.post("/simulate", json={"shocks": {"oil_prices": 0.5}, "duration": 4})
    assert response.status_code == 200
    data = response.json()
    assert "outcomes" in data
    assert "history" in data
    # Oil shock should cause inflation
    assert data["outcomes"]["inflation"] > 0
    # Oil shock should harm manufacturing
    assert data["outcomes"]["manufacturing"] < 0
