
from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


SAMPLE_RESULTS = [
    {
        "source": "Wasalt",
        "property_type": "apartment",
        "transaction_type": "rent",
        "bedrooms": 2,
        "area_sqm": 100,
        "url": "https://example.com/property-1",
        "title": "Apartment 100 SQM with 2 Bedrooms",
    }
]


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_search_endpoint(monkeypatch):
    monkeypatch.setattr(
        routes,
        "search_catalog",
        lambda query, limit: SAMPLE_RESULTS,
    )

    response = client.get(
        "/search",
        params={"q": "2 bedroom apartment rent"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["results"][0]["bedrooms"] == 2


def test_chat_openrouter_success(monkeypatch):
    monkeypatch.setattr(
        routes,
        "search_catalog",
        lambda query, limit: SAMPLE_RESULTS,
    )

    monkeypatch.setattr(
        routes,
        "generate_answer",
        lambda message, results: "Found one matching apartment.",
    )

    response = client.get(
        "/chat",
        params={"message": "2 bedroom apartment rent"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer_source"] == "openrouter"
    assert data["count"] == 1
    assert "matching apartment" in data["answer"]


def test_chat_local_fallback(monkeypatch):
    monkeypatch.setattr(
        routes,
        "search_catalog",
        lambda query, limit: SAMPLE_RESULTS,
    )

    def failing_llm(message, results):
        raise RuntimeError("Simulated OpenRouter failure")

    monkeypatch.setattr(
        routes,
        "generate_answer",
        failing_llm,
    )

    response = client.get(
        "/chat",
        params={"message": "2 bedroom apartment rent"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer_source"] == "local_fallback"
    assert data["count"] == 1


def test_chat_no_results(monkeypatch):
    monkeypatch.setattr(
        routes,
        "search_catalog",
        lambda query, limit: [],
    )

    response = client.get(
        "/chat",
        params={"message": "luxury apartment"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["answer_source"] == "local"
