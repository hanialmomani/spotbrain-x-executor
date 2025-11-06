import os, time, threading
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from binance.client import Client
from binance.exceptions import BinanceAPIException
import requests
import pandas as pd

# ========== مفاتيح Binance ==========
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
EXEC_TOKEN = os.getenv("EXEC_TOKEN", "")  # توكن آمن للربط مع GPT
BASE_SPOT = "https://api.binance.com"

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
app = FastAPI(title="SpotBrain X Executor", version="1.0.0")

WATCH_JOBS = {}  # لمهام المراقبة التلقائية


# نموذج الطلب
class WatchRequest(BaseModel):
    symbol: str
    target_price: float
    action: str  # BUY أو SELL
    timeout_sec: int = 3600


@app.get("/")
def home():
    return {"status": "✅ SpotBrain Executor Active"}


@app.get("/price/{symbol}")
def get_price(symbol: str):
    try:
        data = client.get_symbol_ticker(symbol=symbol.upper())
        return {"symbol": symbol.upper(), "price": data["price"]}
    except BinanceAPIException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/watch_price")
def watch_price(req: WatchRequest, exec_token: str = Header(None)):
    if exec_token != EXEC_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    def job():
        start = time.time()
        while time.time() - start < req.timeout_sec:
            try:
                data = client.get_symbol_ticker(symbol=req.symbol.upper())
                price = float(data["price"])
                if (req.action == "BUY" and price <= req.target_price) or (
                    req.action == "SELL" and price >= req.target_price
                ):
                    print(f"🔔 {req.symbol} reached {price}, executing {req.action}")
                    break
            except Exception as e:
                print("Error:", e)
            time.sleep(10)

    t = threading.Thread(target=job)
    t.start()
    WATCH_JOBS[req.symbol] = {"status": "active", "thread": t.ident}
    return {"message": f"Started watching {req.symbol} for {req.action} at {req.target_price}"}
