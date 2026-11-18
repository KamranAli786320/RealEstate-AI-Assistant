
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

BASE_URL = "https://cdn.wasalt.sa/sitemap/"

SITEMAPS = [
    "product_sitemap_en_sa.xml.gz",
    "rental_pdp_sitemap_en_sa.xml.gz",
]

NAMESPACE = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
}

OUTPUT_FILE = Path("data/raw/wasalt_sitemap_inventory.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def inspect_sitemap(filename: str) -> dict:
    """Inspect a public sitemap and record its URL inventory."""
    url = BASE_URL + filename

    response = requests.get(
        url,
        headers={"User-Agent": "RealEstateAIAssistant/1.0"},
        timeout=(10, 60),
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)

    urls = [
        element.text.strip()
        for element in root.findall(".//sm:loc", NAMESPACE)
        if element.text
    ]

    logging.info("%s: %s URLs discovered", filename, len(urls))

    return {
        "sitemap": filename,
        "sitemap_url": url,
        "total_urls": len(urls),
        "sample_urls": urls[:5],
        "inventory_urls": urls,
    }


def main() -> None:
    """Generate a sitemap inventory report."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    reports = []

    for sitemap in SITEMAPS:
        try:
            reports.append(inspect_sitemap(sitemap))
        except (requests.RequestException, ET.ParseError) as error:
            logging.error("Failed to inspect %s: %s", sitemap, error)

    report = {
        "source": "Wasalt",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collection_type": "Public sitemap URL inventory only",
        "content_extraction": False,
        "sitemaps": reports,
        "total_urls": sum(item["total_urls"] for item in reports),
    }

    OUTPUT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logging.info("Inventory saved to %s", OUTPUT_FILE)
    logging.info("Total URLs: %s", report["total_urls"])


if __name__ == "__main__":
    main()
