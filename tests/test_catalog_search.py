
from app.retrieval import catalog_search


def test_exact_bedroom_rent_filter(monkeypatch):
    records = [
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "rent",
            "bedrooms": 2,
            "url": "https://example.com/apartment-2-bedroom",
            "slug": "apartment-2-bedroom",
        },
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "rent",
            "bedrooms": 1,
            "url": "https://example.com/apartment-1-bedroom",
            "slug": "apartment-1-bedroom",
        },
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "sale",
            "bedrooms": 2,
            "url": "https://example.com/apartment-sale",
            "slug": "apartment-sale",
        },
    ]

    monkeypatch.setattr(
        catalog_search,
        "load_catalog",
        lambda: records,
    )

    results = catalog_search.search_catalog(
        "2 bedroom apartment rent",
        5,
    )

    assert len(results) == 1
    assert results[0]["bedrooms"] == 2
    assert results[0]["transaction_type"] == "rent"
    assert results[0]["property_type"] == "apartment"


def test_three_bedroom_filter(monkeypatch):
    records = [
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "rent",
            "bedrooms": 2,
            "url": "https://example.com/two-bedroom",
            "slug": "two-bedroom",
        },
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "rent",
            "bedrooms": 3,
            "url": "https://example.com/three-bedroom",
            "slug": "three-bedroom",
        },
    ]

    monkeypatch.setattr(
        catalog_search,
        "load_catalog",
        lambda: records,
    )

    results = catalog_search.search_catalog(
        "3 bedroom apartment rent",
        5,
    )

    assert len(results) == 1
    assert results[0]["bedrooms"] == 3


def test_no_matching_bedrooms(monkeypatch):
    records = [
        {
            "source": "Wasalt",
            "property_type": "apartment",
            "transaction_type": "rent",
            "bedrooms": 1,
            "url": "https://example.com/one-bedroom",
            "slug": "one-bedroom",
        },
    ]

    monkeypatch.setattr(
        catalog_search,
        "load_catalog",
        lambda: records,
    )

    results = catalog_search.search_catalog(
        "4 bedroom apartment rent",
        5,
    )

    assert results == []
