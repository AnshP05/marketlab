from pydantic import BaseModel


# Defines the structure for a request to open a position
class openHoldingRequest(BaseModel):
    account_id: int
    ticker: str
    quantity: str