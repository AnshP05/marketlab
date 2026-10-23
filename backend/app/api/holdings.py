from fastapi import APIRouter, HTTPException
from portfolio.errors import InvalidQuantityError
from portfolio import service
from app.api_requests import openHoldingRequest
import sqlite3

router = APIRouter(prefix="/api/v1/holdings")

@router.get("")
def holdings():
    return {"holdings" : service.get_holdings()}

@router.post("/opening", status_code=201)
def open_holding(request: openHoldingRequest):
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