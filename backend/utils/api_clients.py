import os
import pandas as pd
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load .env variables
load_dotenv()

# ---------------------------------------
# PATH TO DATASET
# ---------------------------------------
DATASET_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/dataset.csv")
)

# ---------------------------------------
# LOAD CSV ONCE (FAST)
# ---------------------------------------
try:
    NEWS_DF = pd.read_csv(DATASET_PATH)
except Exception as e:
    print("❌ ERROR LOADING DATASET:", e)
    NEWS_DDF = pd.DataFrame()

# ---------------------------------------
# API FETCHER (only used by collect_data.py)
# ---------------------------------------
def fetch_news_from_api(ticker, limit=50):
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    url = "https://newsapi.org/v2/everything"

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
        r = requests.get(url, params=params, timeout=25)
        r.raise_for_status()
        articles = r.json().get("articles", [])

        formatted = []
        for a in articles:
            formatted.append({
                "ticker": ticker.upper(),
                "headline": a.get("title"),
                "summary": a.get("description"),
                "url": a.get("url"),
                "date": a.get("publishedAt"),
                "source": a.get("source", {}).get("name")
            })

        return formatted

    except Exception as e:
        print(f"API error for {ticker}: {e}")
        return []


# ---------------------------------------
# DATASET FETCHER (used by main.py in production)
# ---------------------------------------
def fetch_news_from_dataset(ticker, limit=10):
    ticker = ticker.upper()

    try:
        df = NEWS_DF[NEWS_DF["ticker"] == ticker]
    except Exception:
        print("❌ Dataset not loaded properly")
        return []

    if df.empty:
        print("⚠️ No dataset news for", ticker)
        return []

    # sort newest → oldest
    df = df.sort_values("date", ascending=False).head(limit)

    results = []
    for _, row in df.iterrows():
        results.append({
            "title": row.get("headline"),
            "snippet": row.get("summary"),
            "url": row.get("url")
        })

    return results


# ---------------------------------------
# WRAPPER (main function used by backend)
# ---------------------------------------
def fetch_news_for_ticker(ticker, limit=10):
    """
    On Render/production we only use dataset (faster and no API limits)
    """
    return fetch_news_from_dataset(ticker, limit)
