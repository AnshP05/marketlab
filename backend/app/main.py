from fastapi import FastAPI 
from app.api.holdings import router as holdings_router
from app.api.accounts import router as accounts_router


app = FastAPI()
app.include_router(holdings_router)
app.include_router(accounts_router)

@app.get("/health")
def health():
    return {"status" : "ok"}