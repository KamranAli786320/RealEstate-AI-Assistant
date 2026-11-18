
def build_chat_response(message: str, results: list[dict]) -> str:
    """Build readable answers from retrieved property records."""

    if not results:
        return (
            "I couldn't find matching properties. "
            "Try changing your search criteria."
        )

    verified = [
        item for item in results
        if item.get("verification_status") == "verified_from_page"
    ]

    selected = verified + [
        item for item in results
        if item not in verified
    ]

    lines = [f"I found {len(results)} matching property records."]

    for index, item in enumerate(selected[:5], start=1):
        lines.append(f"\nProperty {index}:")

        title = item.get("title")
        if title:
            lines.append(f"Title: {title}")

        if item.get("area_sqm") is not None:
            lines.append(f"Area: {item['area_sqm']} SQM")

        if item.get("bedrooms") is not None:
            lines.append(f"Bedrooms: {item['bedrooms']}")

        if item.get("price") is not None:
            currency = item.get("currency", "SAR")
            period = item.get("price_period", "")
            lines.append(
                f"Price: {item['price']:,.0f} {currency}"
                + (f" per {period}" if period else "")
            )

        if item.get("transaction_type"):
            lines.append(
                f"Transaction: {item['transaction_type']}"
            )

        if item.get("url"):
            lines.append(f"Source: {item['url']}")

    return "\n".join(lines)
