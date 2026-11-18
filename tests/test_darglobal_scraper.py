from app.scrapers.darglobal_scraper import DarGlobalScraper


def test_parse_page_title() -> None:
    scraper = DarGlobalScraper()

    html = """
    <html>
        <head>
            <title>DarGlobal Projects</title>
        </head>
    </html>
    """

    result = scraper.parse_page_title(html)

    assert result == "DarGlobal Projects"