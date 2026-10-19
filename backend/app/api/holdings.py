from fastapi import APIRouter
from portfolio.service import get_holdings

router = APIRouter(prefix="/api/v1/holdings")

@router.get("")
def holdings():
    return {"holdings" : get_holdings()}