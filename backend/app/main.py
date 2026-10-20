from fastapi import FastAPI 
from app.api.holdings import router as holdings_router
from app.api.accounts import router as accounts_router
from pathlib import Path
from fastapi.responses import FileResponse

html_path = (Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html")


app = FastAPI()
app.include_router(holdings_router)
app.include_router(accounts_router)

@app.get("/health")
def health():
    return {"status" : "ok"}
@app.get("/")
def homepage():
    return FileResponse(html_path)