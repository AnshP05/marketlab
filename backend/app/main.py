from fastapi import FastAPI 
from app.api.holdings import router as holdings_router


app = FastAPI()
app.include_router(holdings_router)


@app.get("/health")
def health():
    return {"status" : "ok"}