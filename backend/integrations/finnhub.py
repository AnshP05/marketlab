from portfolio.models import Quote
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from decimal import Decimal
from datetime import datetime, timezone
from portfolio.errors import FinnHubAPIError

def fetch_quote(symbol: str) -> Quote:
    finnhub_api_key = os.environ["FINNHUB_API_KEY"]
    query = urlencode({"symbol": symbol})
    url = f"https://finnhub.io/api/v1/quote?{query}"
    request = Request(
        url,
        headers={"X-Finnhub-Token":finnhub_api_key}
    )

    with urlopen(request, timeout=10) as response:
        body = response.read()

    data = json.loads(body, parse_float=Decimal)
    if not isinstance(data, dict):
        raise FinnHubAPIError("Unexpected quote reponse format.")
    price = data.get("c")
    if isinstance(price, bool) or not isinstance(price, (int, Decimal)):
        raise FinnHubAPIError("Quote price is missing or invalid.")

    price = Decimal(price)
    if not price.is_finite() or price <= 0:
        raise FinnHubAPIError("Quote price must be finited and greater than zero")

    timestamp = data.get("t")

    if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp <= 0:
        raise FinnHubAPIError("Timestamp is missing or invalid.")

    try:
        as_of = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (ValueError, OverflowError, OSError) as e:
        raise FinnHubAPIError("Quote timestamp is invalid.") from e

    quote = Quote(
        symbol=symbol,
        price=price,
        currency="USD",
        as_of=as_of,
        source="Finnhub"
    )
    return quote
