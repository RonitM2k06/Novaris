from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_ontology_endpoint():
    response = client.get("/ontology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    # Verify core nodes exist
    node_ids = [n["id"] for n in data["nodes"]]
    assert "gdp" in node_ids
    assert "inflation" in node_ids
    assert len(data["edges"]) > 0
