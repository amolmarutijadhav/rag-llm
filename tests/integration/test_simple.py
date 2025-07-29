import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

def test_simple_endpoint(async_client):
    """Test that basic FastAPI testing works."""
    response = async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_simple_math():
    """Test that basic pytest functionality works."""
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world" 