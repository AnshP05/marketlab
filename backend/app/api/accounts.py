from fastapi import APIRouter, HTTPException
from portfolio.service import get_accounts, open_account
from app.api_requests import OpenAccountRequest
from portfolio.errors import InvalidAccountNameError
import sqlite3

router = APIRouter(prefix="/api/v1/accounts")

@router.get("")
def accounts():
    return {"accounts" : get_accounts()}

@router.post("",status_code=201)
def create_account(request: OpenAccountRequest):
    account_name = request.name
    try:
        account_id = open_account(account_name)
    except InvalidAccountNameError as e:
        raise HTTPException(
                    status_code=422,
                    detail=str(e)
            ) from e
    except sqlite3.IntegrityError as e:
        if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise HTTPException(
                        status_code=409,
                        detail="Cannot have duplicate account name"
                    ) from e
        else:
            raise HTTPException(
                            status_code=500,
                            detail="Unable to create new account."
                        ) from e
    except sqlite3.Error as e:
        raise HTTPException(
                        status_code=500,
                        detail="Unable to create new account."
                    ) from e


    return {"account_id": account_id}