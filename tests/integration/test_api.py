# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

def test_get_train_delays_map(client):
    response = client.get("/train_delays_map")
    assert response.status_code in [200, 404]
    
def test_get_station_busyness(client):
    response = client.get("/station_busyness/KGX")
    assert response.status_code == 200
    assert "busyness_score" in response.json()