
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def extract_area(slug: str) -> dict:
    """
    Extract area from a property URL slug.

    Short numeric values are preserved as integers.
    Longer values are treated as ambiguous because Wasalt
    removes decimal separators from some URL slugs.
    """
    area_match = re.search(r"-(\d+)-sqm", slug)

    if not area_match:
        return {
            "area_sqm": None,
            "area_slug_raw": None,
            "area_parse_status": "not_found",
        }

    raw_value = area_match.group(1)

    if len(raw_value) <= 3:
        return {
            "area_sqm": int(raw_value),
            "area_slug_raw": raw_value,
            "area_parse_status": "parsed_integer",
        }

    return {
        "area_sqm": None,
        "area_slug_raw": raw_value,
        "area_parse_status": "ambiguous_decimal_format",
    }


def process_darglobal():
    """Process public DarGlobal sitemap URL metadata."""
    file_path = RAW_DIR / "darglobal_sitemap_inventory.json"
    data = json.loads(file_path.read_text(encoding="utf-8"))

    records = []

    for url in data.get("urls", []):
        parts = urlparse(url).path.strip("/").split("/")
        country = ""
        property_type = "unspecified"

        for part in parts:
            if part.startswith("properties-in-"):
                country = part.replace("properties-in-", "")

            if part in ("villas", "apartments"):
                property_type = part

        records.append({
            "source": "DarGlobal",
            "url": url,
            "country": country,
            "property_type": property_type,
            "record_type": "category_url",
        })

    return records


def process_wasalt():
    """Process public Wasalt sitemap URL metadata."""
    file_path = RAW_DIR / "wasalt_sitemap_inventory.json"
    data = json.loads(file_path.read_text(encoding="utf-8"))

    records = []

    for sitemap in data.get("sitemaps", []):
        for url in sitemap.get("inventory_urls", []):
            path = urlparse(url).path
            slug = path.strip("/").split("/")[-1]

            if "/sale/" in path:
                transaction = "sale"
            elif "/rent/" in path:
                transaction = "rent"
            elif "/dailyrental/" in path:
                transaction = "daily_rental"
            else:
                transaction = "unspecified"

            bedroom_match = re.search(
                r"-(\d+)-bedrooms?",
                slug,
            )

            area_data = extract_area(slug)

            records.append({
                "source": "Wasalt",
                "url": url,
                "transaction_type": transaction,
                "property_type": slug.split("-")[0],
                "area_sqm": area_data["area_sqm"],
                "area_slug_raw": area_data["area_slug_raw"],
                "area_parse_status": area_data["area_parse_status"],
                "bedrooms": (
                    int(bedroom_match.group(1))
                    if bedroom_match else None
                ),
                "slug": slug,
                "record_type": "property_url",
            })

    return records


def main():
    """Build the local property URL catalogue."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = process_darglobal() + process_wasalt()

    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "collection_type": "Public sitemap URL metadata",
        "page_content_extracted": False,
        "total_records": len(records),
        "records": records,
    }

    output_file = OUTPUT_DIR / "property_url_catalog.json"

    output_file.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Catalog created successfully.")
    print("Total records:", len(records))
    print("Output:", output_file)

    wasalt_records = [
        record for record in records
        if record.get("source") == "Wasalt"
    ]

    ambiguous = sum(
        record["area_parse_status"] == "ambiguous_decimal_format"
        for record in wasalt_records
    )

    parsed = sum(
        record["area_parse_status"] == "parsed_integer"
        for record in wasalt_records
    )

    print("Wasalt areas parsed as integers:", parsed)
    print("Wasalt areas needing verification:", ambiguous)


if __name__ == "__main__":
    main()
