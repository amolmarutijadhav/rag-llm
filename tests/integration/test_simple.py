import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create a simple FastAPI app for testing
app = FastAPI()

@app.get("/test")
def test_endpoint():
    return {"status": "ok", "message": "test"}

def test_simple_endpoint():
    """Test that basic FastAPI testing works."""
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "test"

def test_simple_math():
    """Test that basic pytest functionality works."""
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world" 