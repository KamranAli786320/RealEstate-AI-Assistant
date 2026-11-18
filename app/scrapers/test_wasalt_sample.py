
import requests
from bs4 import BeautifulSoup

URLS = [
    "https://wasalt.sa/en/property/sale/apartment-279-sqm-with-6-bedrooms-5856616",
    "https://wasalt.sa/en/property/sale/floor-125-sqm-with-3-bedrooms-5856629",
    "https://wasalt.sa/en/property/rent/floor-110-sqm-with-2-bedrooms-5856632",
]

for url in URLS:
    print("\nURL:", url)

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "RealEstateAIAssistant/1.0"},
            timeout=20,
        )

        print("Status:", response.status_code)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print("Title:", soup.title.get_text(strip=True) if soup.title else "Not found")
            print("Page length:", len(response.text))
        else:
            print("Page not accessible.")

    except requests.RequestException as error:
        print("Request failed:", error)
