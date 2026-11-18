
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DarGlobalScraper:
    """Fetch publicly accessible DarGlobal project information."""

    BASE_URL = "https://darglobal.co.uk"
    PROJECTS_URL = f"{BASE_URL}/projects/"
    SITEMAP_URL = f"{BASE_URL}/sitemap.xml"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "RealEstateAIAssistant/1.0"
        })

    def _fetch_url(self, url: str) -> str:
        """Fetch a permitted public URL and validate its response."""

        parsed_url = urlparse(url)

        if parsed_url.netloc != urlparse(self.BASE_URL).netloc:
            raise ValueError("URL must belong to DarGlobal.")

        response = self.session.get(
            url,
            timeout=20,
        )
        response.raise_for_status()

        content = response.text

        # Detect security challenge pages instead of treating
        # them as actual website content.
        if "_Incapsula_Resource" in content:
            logger.warning("Security challenge detected for %s", url)
            raise RuntimeError(
                "DarGlobal returned a security challenge. "
                "Automated access is not available."
            )

        return content

    def fetch_projects_page(self) -> str:
        """Fetch the public projects page."""

        html = self._fetch_url(self.PROJECTS_URL)

        logger.info("DarGlobal projects page fetched successfully")

        return html

    def fetch_sitemap(self) -> str:
        """Fetch the publicly accessible XML sitemap."""

        xml = self._fetch_url(self.SITEMAP_URL)

        if "<urlset" not in xml and "<sitemapindex" not in xml:
            raise ValueError(
                "The response is not a valid XML sitemap."
            )

        logger.info("DarGlobal sitemap fetched successfully")

        return xml
    def extract_project_urls(self, xml: str) -> list[str]:
        """Extract project URLs from the sitemap."""

        root = ET.fromstring(xml)

        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        project_urls = []

        for element in root.findall(".//sm:loc", namespace):
            url = element.text

            if not url:
                continue

            path = urlparse(url).path.lower()

            if "/projects/" in path:
                project_urls.append(url)

        logger.info(
            "Found %s project URLs in sitemap",
            len(project_urls),
        )

        return project_urls

    def parse_page_title(self, html: str) -> str:
        """Extract the HTML page title."""

        soup = BeautifulSoup(html, "html.parser")

        if soup.title:
            return soup.title.get_text(strip=True)

        return "Title not found"
