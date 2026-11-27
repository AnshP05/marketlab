from fastapi import HTTPException, APIRouter
from portfolio.errors import FinnHubAPIError
from integrations.finnhub import fetch_quote
from portfolio.models import Quote

router = APIRouter(prefix="/api/v1/live-quotes")

@router.get("")
def get_live_quote(symbol: str):
    try:
        quote = fetch_quote(symbol)
    except FinnHubAPIError as e:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve a quote from Finnhub"
        )

    return {
        "symbol" : quote.symbol,
        "price" : str(quote.price),
        "currency" : quote.currency,
        "as_of" : quote.as_of,
        "source" : quote.source
    }