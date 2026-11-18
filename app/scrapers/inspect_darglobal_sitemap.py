
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.scrapers.darglobal_scraper import DarGlobalScraper

OUTPUT_FILE = Path("data/raw/darglobal_sitemap_inventory.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    scraper = DarGlobalScraper()

    try:
        xml = scraper.fetch_sitemap()
        urls = scraper.extract_project_urls(xml)

        report = {
            "source": "DarGlobal",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "collection_type": "Public sitemap URL inventory only",
            "content_extraction": False,
            "total_urls": len(urls),
            "urls": urls,
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logging.info("Total project-category URLs: %s", len(urls))
        logging.info("Inventory saved to %s", OUTPUT_FILE)

        for url in urls[:5]:
            print(url)

    except (RuntimeError, ValueError, OSError) as error:
        logging.error("DarGlobal inventory failed: %s", error)


if __name__ == "__main__":
    main()
