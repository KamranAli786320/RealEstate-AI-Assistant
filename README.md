# EstateIQ — AI-Powered Real Estate Assistant

EstateIQ is an AI-powered real estate discovery assistant built with Python, FastAPI, and OpenRouter. It helps users search property records and ask natural-language questions about available property information.

**Live Demo:** https://real-estate-ai-assistant-beta.vercel.app

**GitHub:** https://github.com/KamranAli786320/RealEstate-AI-Assistant

## Features

- Real estate property search using natural-language queries.
- Property filtering by type, transaction, and bedroom count.
- AI-generated responses using an OpenRouter-hosted language model.
- Local fallback responses when the AI service is unavailable.
- Source URLs included with property results.
- Verification-aware responses that distinguish confirmed listing details from sitemap metadata.
- FastAPI backend and responsive web interface.
- Docker containerization.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Search | Scikit-learn, TF-IDF |
| LLM Integration | OpenRouter API |
| Data Extraction | Requests, BeautifulSoup |
| Deployment | Vercel |
| Containerization | Docker |
| Testing | Pytest |

## Data Sources

The project investigates publicly accessible property information and sitemap inventories from:

- [DarGlobal](https://darglobal.co.uk/)
- [Wasalt](https://wasalt.sa/)

The collected catalogue contains 62,683 property URL records:
- DarGlobal: 14 sitemap URLs.
- Wasalt: 62,669 sitemap URLs.

One Wasalt property has been manually verified from its listing page and
