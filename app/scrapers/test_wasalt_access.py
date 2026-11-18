
import requests
from bs4 import BeautifulSoup

TERMS_URL = "https://wasalt.sa/en/s/terms-of-use"

KEYWORDS = [
    "scrape",
    "crawling",
    "automated",
    "robot",
    "copy",
    "reproduce",
    "commercial",
    "intellectual property",
    "third party",
    "data mining",
]


def inspect_terms() -> None:
    """Find relevant usage restrictions in Wasalt's Terms of Use."""
    try:
        response = requests.get(
            TERMS_URL,
            headers={"User-Agent": "RealEstateAIAssistant/1.0"},
            timeout=(5, 20),
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        print("Status:", response.status_code)
        print("Page title:", soup.title.get_text(strip=True) if soup.title else "Not found")
        print("Total text length:", len(text))

        for keyword in KEYWORDS:
            position = text.lower().find(keyword)

            if position != -1:
                start = max(0, position - 250)
                end = min(len(text), position + 500)

                print(f"\n--- {keyword.upper()} ---")
                print(text[start:end])

    except requests.RequestException as error:
        print("Request failed:", error)


if __name__ == "__main__":
    inspect_terms()
