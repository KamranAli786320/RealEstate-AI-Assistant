
import json
import re

from functools import lru_cache
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CATALOG_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "property_url_catalog.json"
)

VERIFIED_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "verified_wasalt_samples.json"
)

STOP_WORDS = {
    "for", "in", "with", "the", "a", "an", "to",
    "near", "me", "bedroom", "bedrooms",
    "sqm", "square", "meter", "meters",
}


def tokenize(text: str) -> set[str]:
    text = text.lower().replace("dailyrental", "daily rental")
    return set(re.findall(r"[a-z0-9]+", text))


def load_catalog() -> list[dict]:
    """Load sitemap metadata and verified property samples."""

    with CATALOG_FILE.open(encoding="utf-8") as file:
        records = json.load(file)["records"]

    if VERIFIED_FILE.exists():
        with VERIFIED_FILE.open(encoding="utf-8") as file:
            verified = json.load(file)

        records.extend(verified.get("records", []))

    return records


def build_search_document(record: dict) -> str:
    """Create searchable text from property metadata."""

    fields = [
        record.get("source", ""),
        record.get("country", ""),
        record.get("property_type", ""),
        record.get("transaction_type", ""),
        record.get("slug", ""),
        record.get("title", ""),
        record.get("area_sqm", ""),
        record.get("bedrooms", ""),
        record.get("price", ""),
        urlparse(record.get("url", "")).path,
    ]

    return " ".join(
        str(value)
        for value in fields
        if value is not None
    )


@lru_cache(maxsize=4)
def build_search_index(loader: Callable) -> tuple:
    """
    Build and cache the TF-IDF index.

    Passing the loader as a cache key also keeps tests using
    mocked catalog loaders independent from the real catalog.
    """

    records = loader()

    documents = [
        build_search_document(record)
        for record in records
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=100000,
    )

    matrix = vectorizer.fit_transform(documents)

    return records, vectorizer, matrix


def normalize_property_type(value: str) -> str:
    """Normalize common property type variations."""

    value = value.lower().strip()

    aliases = {
        "apartments": "apartment",
        "flat": "apartment",
        "flats": "apartment",
        "villas": "villa",
        "floors": "floor",
    }

    return aliases.get(value, value)


def extract_filters(query: str) -> dict:
    """Extract exact property constraints from the query."""

    text = query.lower()

    bedroom_match = re.search(
        r"\b(\d+)\s*[- ]?\s*bedrooms?\b",
        text,
    )

    transaction = None

    if re.search(r"\b(rent|rental|lease)\b", text):
        transaction = "rent"
    elif re.search(r"\b(sale|buy|purchase)\b", text):
        transaction = "sale"

    property_type = None

    if re.search(r"\b(apartment|apartments|flat|flats)\b", text):
        property_type = "apartment"
    elif re.search(r"\b(villa|villas)\b", text):
        property_type = "villa"
    elif re.search(r"\b(floor|floors)\b", text):
        property_type = "floor"

    return {
        "bedrooms": (
            int(bedroom_match.group(1))
            if bedroom_match else None
        ),
        "transaction_type": transaction,
        "property_type": property_type,
    }


def matches_filters(record: dict, filters: dict) -> bool:
    """Apply exact filters before relevance ranking."""

    bedrooms = filters["bedrooms"]

    if bedrooms is not None:
        if record.get("bedrooms") != bedrooms:
            return False

    transaction = filters["transaction_type"]

    if transaction:
        if record.get("transaction_type") != transaction:
            return False

    property_type = filters["property_type"]

    if property_type:
        record_type = normalize_property_type(
            str(record.get("property_type", ""))
        )

        if record_type != property_type:
            return False

    return True


def search_catalog(query: str, limit: int = 5) -> list[dict]:
    """
    Search using exact filters and TF-IDF relevance ranking.

    The index is built once and reused for subsequent searches.
    """

    query = query.strip()

    if not query:
        return []

    filters = extract_filters(query)

    records, vectorizer, matrix = build_search_index(load_catalog)

    matching_indexes = [
        index
        for index, record in enumerate(records)
        if matches_filters(record, filters)
    ]

    if not matching_indexes:
        return []

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        matrix[matching_indexes],
    ).flatten()

    ranked_results = sorted(
        zip(scores, matching_indexes),
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        records[index]
        for score, index in ranked_results[:limit]
    ]
