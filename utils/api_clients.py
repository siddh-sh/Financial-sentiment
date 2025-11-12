import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ===============================
# API KEYS
# ===============================
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
ALPHA_KEY = os.getenv("ALPHAVANTAGE_KEY")

# ===============================
# API BASE URLs
# ===============================
BASE_NEWS = "https://newsapi.org/v2/everything"
BASE_ALPHA = "https://www.alphavantage.co/query"

# ===============================
# FETCH NEWS (NewsAPI only)
# ===============================
def fetch_newsapi_news(ticker, limit=60):
    """
    Fetch recent news articles for a ticker using NewsAPI.
    """
    from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    params = {
        "q": ticker,
        "language": "en",
        "from": from_date,
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": NEWSAPI_KEY
    }

    try:
        r = requests.get(BASE_NEWS, params=params, timeout=30)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        formatted = []
        for art in articles:
            formatted.append({
                "title": art.get("title"),
                "snippet": art.get("description"),
                "url": art.get("url"),
                "source": art.get("source", {}).get("name"),
                "published_at": art.get("publishedAt")
            })
        return formatted
    except Exception as e:
        print(f"[{ticker}] NewsAPI fetch error: {e}")
        return []

# ===============================
# WRAPPER FUNCTION
# ===============================
def fetch_news_for_ticker(ticker, limit=60):
    """
    Wrapper so we can easily add new sources in future.
    """
    return fetch_newsapi_news(ticker, limit=limit)

# ===============================
# FETCH DAILY OHLC FROM ALPHA VANTAGE
# ===============================
import yfinance as yf

def fetch_alpha_daily(symbol):
    """
    Fetch daily OHLC close prices using Yahoo Finance.
    Returns {date: close_price}
    """
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        prices = {}
        for date, row in df.iterrows():
            prices[str(date.date())] = float(row["Close"])
        if not prices:
            print(f"[{symbol}] ⚠️ No price data fetched from Yahoo Finance.")
        return prices
    except Exception as e:
        print(f"[{symbol}] Yahoo Finance fetch error: {e}")
        return {}

