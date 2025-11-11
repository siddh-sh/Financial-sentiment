# collect_data.py
import os
import json
from datetime import datetime
from dotenv import load_dotenv

import pandas as pd

from utils.api_clients import fetch_news_for_ticker, fetch_alpha_daily
from utils.text import clean_text, merge_fields
from utils.labeling import label_news_item

# ---------------------------
# Config
# ---------------------------
load_dotenv()
TICKERS = os.getenv("DEFAULT_TICKERS", "AAPL,TSLA,NVDA,MSFT").split(",")
NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", "40"))

DATA_DIR = "data"
DATASET_CSV = os.path.join(DATA_DIR, "dataset.csv")

# ---------------------------
# Helpers
# ---------------------------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def iso_date_from_ts(ts: str) -> str:
    # Marketaux usually returns ISO timestamp; keep the YYYY-MM-DD part
    # Example: "2025-11-07T13:45:00Z" -> "2025-11-07"
    if not ts:
        return ""
    return ts[:10]

# ---------------------------
# Main
# ---------------------------
def main():
    ensure_data_dir()

    # Load existing dataset if present
    if os.path.exists(DATASET_CSV):
        df_all = pd.read_csv(DATASET_CSV)
    else:
        df_all = pd.DataFrame(columns=[
            "ticker", "date", "headline", "summary",
            "url", "source", "text", "label"
        ])

    rows_new = []

    for tk in TICKERS:
        # 1) Fetch latest news for ticker
        try:
            news_items = fetch_news_for_ticker(tk, limit=NEWS_LIMIT)
        except Exception as e:
            print(f"[{tk}] News fetch error: {e}")
            continue

        # 2) Fetch / cache OHLC for ticker
        try:
            prices = fetch_alpha_daily(tk)
        except Exception as e:
            print(f"[{tk}] Price fetch error: {e}")
            prices = {}

        # 3) Build labeled rows
        for n in news_items:
            headline = (n.get("title") or "").strip()
            summary  = (n.get("snippet") or n.get("description") or "").strip()
            url      = (n.get("url") or "").strip()
            source   = (n.get("source") or "").strip()
            published_at = n.get("published_at")

            if not headline or not url:
                continue  # skip unusable entries

            d0 = iso_date_from_ts(published_at)
            if not d0:
                continue

            # Label using next trading day close vs base day close
            y = label_news_item(d0, prices)
            if y is None:
                continue  # skip unlabeled

            text_merged = merge_fields(headline, summary)
            text_clean  = clean_text(text_merged)

            rows_new.append({
                "ticker": tk,
                "date": d0,
                "headline": headline,
                "summary": summary,
                "url": url,
                "source": source,
                "text": text_clean,
                "label": int(y)
            })

        print(f"[{tk}] collected: {len(rows_new)} total new so far")

    # 4) Append + deduplicate by URL
    if rows_new:
        df_new = pd.DataFrame(rows_new)
        # Concatenate then drop duplicates by URL
        combined = pd.concat([df_all, df_new], ignore_index=True)
        before = len(combined)
        combined = combined.drop_duplicates(subset=["url"]).reset_index(drop=True)
        after = len(combined)
        removed = before - after

        combined.to_csv(DATASET_CSV, index=False)
        print(f"Saved dataset -> {DATASET_CSV}")
        print(f"Rows added: {len(df_new)} | Duplicates removed: {removed} | Total rows now: {after}")
    else:
        print("No new labeled rows this run.")

if __name__ == "__main__":
    main()
