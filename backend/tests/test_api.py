"""Integration test suite for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_health_endpoint():
    """Test GET /health API endpoint response structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "ollama" in data
    assert "vector_store" in data
    assert "embedding_model" in data


def test_get_documents_endpoint():
    """Test GET /documents API endpoint response structure."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()

    assert "documents" in data
    assert "total_count" in data
    assert isinstance(data["documents"], list)


def test_chat_invalid_payload():
    """Test POST /chat error validation for empty question query."""
    response = client.post("/chat", json={"question": "   "})
    assert response.status_code in (400, 422)


def test_sources_not_found():
    """Test GET /sources/{id} for non-existent document ID."""
    response = client.get("/sources/non_existent_doc_999.pdf")
    assert response.status_code == 404


def test_delete_document_not_found():
    """Test DELETE /documents/{id} for non-existent document ID."""
    response = client.delete("/documents/non_existent_doc_999.pdf")
    assert response.status_code == 404

