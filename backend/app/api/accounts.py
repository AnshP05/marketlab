from fastapi import APIRouter
from portfolio.service import get_accounts

router = APIRouter(prefix="/api/v1/accounts")

@router.get("")
def accounts():
    return {"accounts" : get_accounts()}