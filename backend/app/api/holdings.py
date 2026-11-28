from fastapi import APIRouter, HTTPException
from portfolio.errors import InvalidQuantityError, InvalidPositionIdError, FinnHubAPIError
from portfolio.service import get_holding, get_accounts, get_holding_value, get_holdings, get_opening_positions
from app.api_requests import OpenHoldingRequest
import sqlite3
from portfolio import service
from portfolio.models import HoldingValue

router = APIRouter(prefix="/api/v1/holdings")

@router.get("")
def holdings():
    return {"holdings" : get_holdings()}

@router.get("/opening-positions")
def opening_positions():
    try:
        opening_positions_list = get_opening_positions()
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail="Unable to load opening positions."
        )
    return {"opening-positions": opening_positions_list}


@router.post("/opening", status_code=201)
def open_holding(request: OpenHoldingRequest):
    #Parse the json req as of now we don't need an account since its all under one account
    # We would need what brokerage(i.e. Wells Fargo, Robinhood), stock ticker(i.e. MSFT, AAPL)
    # timestamp(we can abstract to future for now), buy price, shares
    account_id = request.account_id
    ticker = request.ticker
    quantity = request.quantity
    
    # send request to the repository with the parsed data
    try:
        position_id = service.open_holding(account_id, ticker, quantity)
    # Catch any errors and raise them for the frontend to display to the user with 
    except InvalidQuantityError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        ) from e
    except sqlite3.IntegrityError as e:
        if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise HTTPException(
                        status_code=409,
                        detail="An opening position already exists for this account and ticker."
                    ) from e
        elif e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY:
            raise HTTPException(
                status_code=404,
                detail="Account not found."
            ) from e
        else:
            raise HTTPException(
                status_code=500,
                detail="Unable to save the opening position."
            ) from e
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail="Unable to save the opening position."
        ) from e
        
    
    return {"position_id" : position_id}

@router.get("/value")
def holding_value(position_id: int):
    try:
        holding_value = service.get_holding_value(position_id)

        return {
            "symbol" : holding_value.symbol,
            "value" : str(holding_value.value),
            "currency" : holding_value.currency,
            "as_of" : holding_value.as_of,
            "source" : holding_value.source
        }
    except InvalidPositionIdError as e:
        raise HTTPException(
            status_code=404,
            detail="No saved holding has that ID."
        )
    except FinnHubAPIError as e:
        raise HTTPException(
            status_code=502,
            detail="Finnhub couldn't provide a useable quote"
        )
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail="The database lookup failed"
        )
