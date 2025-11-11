import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta



load_dotenv()

MARKETAUX_KEY = os.getenv("MARKETAUX_API_KEY")
ALPHA_KEY     = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_NEWS = "https://api.marketaux.com/v1/news/all"
BASE_ALPHA = "https://www.alphavantage.co/query"

def fetch_news_for_ticker(ticker, limit=40):
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    params = {
        "api_token": MARKETAUX_KEY,
        "search": ticker,
        "limit": limit,
        "countries": "us",
        "language": "en",
        "sort": "published_at:desc",
        "published_after" : thirty_days_ago
    }
    r = requests.get(BASE_NEWS, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

def fetch_alpha_daily(symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": ALPHA_KEY
    }
    r = requests.get(BASE_ALPHA, params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get("Time Series (Daily)", {})
    return {d: float(v["4. close"]) for d, v in data.items()}
