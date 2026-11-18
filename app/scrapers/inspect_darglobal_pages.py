
import json
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

INPUT_FILE = Path("data/raw/darglobal_sitemap_inventory.json")

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def main() -> None:
    inventory = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    urls = inventory["urls"]

    session = requests.Session()
    session.headers.update({
        "User-Agent": "RealEstateAIAssistant/1.0"
    })

    for url in urls:
        print(f"\nURL: {url}")

        try:
            response = session.get(url, timeout=(10, 25))
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.get_text(strip=True) if soup.title else "Not found"
            blocked = "_Incapsula_Resource" in response.text

            print("Status:", response.status_code)
            print("Title:", title)
            print("HTML length:", len(response.text))
            print("Security challenge:", blocked)

            if not blocked and response.ok:
                print("Page preview:", soup.get_text(" ", strip=True)[:300])

        except requests.RequestException as error:
            logging.warning("Request failed: %s", error)


if __name__ == "__main__":
    main()
