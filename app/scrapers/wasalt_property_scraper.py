
import json
import re
import requests

from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def extract_number(text):
    """Extract a numeric value from text."""
    if not text:
        return None

    match = re.search(r"[\d,]+(?:\.\d+)?", text)

    if not match:
        return None

    return float(match.group().replace(",", ""))


def scrape_property(url):
    """Extract publicly visible property information from Wasalt."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    title = soup.title.get_text(strip=True) if soup.title else None

    if (
        "_Incapsula_Resource" in response.text
        or "Just a moment..." in page_text
    ):
        raise RuntimeError(
            "Security challenge detected. Scraping stopped."
        )

    area = None
    bedrooms = None
    price = None

    area_match = re.search(
        r"([\d,]+(?:\.\d+)?)\s*SQM",
        page_text,
        re.IGNORECASE,
    )

    bedroom_match = re.search(
        r"(\d+)\s*bedrooms?",
        page_text,
        re.IGNORECASE,
    )

    price_match = re.search(
        r"Price:\s*([\d,]+(?:\.\d+)?)\s*SAR",
        page_text,
        re.IGNORECASE,
    )

    if area_match:
        area = float(area_match.group(1).replace(",", ""))

    if bedroom_match:
        bedrooms = int(bedroom_match.group(1))

    if price_match:
        price = float(price_match.group(1).replace(",", ""))

    return {
        "source": "Wasalt",
        "url": url,
        "title": title,
        "area_sqm": area,
        "bedrooms": bedrooms,
        "price_sar": price,
        "content_extraction_status": (
            "success" if area is not None else "area_not_found"
        ),
    }


if __name__ == "__main__":
    test_url = (
        "https://wasalt.sa/en/property/rent/"
        "apartment-10372-sqm-with-2-bedrooms-5924260"
    )

    try:
        result = scrape_property(test_url)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as error:
        print("Scraping error:", error)
