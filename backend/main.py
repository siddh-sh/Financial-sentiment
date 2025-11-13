from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import joblib, os, pandas as pd

from backend.utils.api_clients import fetch_news_for_ticker
from backend.utils.text import clean_text, merge_fields

app = FastAPI(title="SentimentIQ")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve static files (CSS, JS, images)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ✅ Serve the main frontend page
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Load model + vectorizer
MODEL = joblib.load(os.path.join(os.path.dirname(__file__), "models", "svm_model.joblib"))
VECTORIZER = joblib.load(os.path.join(os.path.dirname(__file__), "models", "tfidf_vectorizer.joblib"))

class RequestBody(BaseModel):
    ticker: str
    limit: int = 10

@app.post("/predict")
def predict_stock_sentiment(request: RequestBody):
    ticker = request.ticker.upper()
    print(f"📩 Predict request for: {ticker}")
    try:
        news_items = fetch_news_for_ticker(ticker, request.limit)
        if not news_items:
            return JSONResponse({"error": f"No news found for {ticker}"}, status_code=404)
        results = []
        for item in news_items:
            headline = (item.get("title") or "").strip()
            summary = (item.get("snippet") or "").strip()
            merged = merge_fields(headline, summary)
            cleaned = clean_text(merged)
            vector = VECTORIZER.transform([cleaned])
            pred = MODEL.predict(vector)[0]
            prob = MODEL.predict_proba(vector)[0][1]
            results.append({
                "headline": headline,
                "direction": "Bullish" if pred == 1 else "Bearish",
                "prob": round(float(prob), 2),
                "url": item.get("url", "#")
            })
        bullish_prob = sum(r["prob"] for r in results) / len(results)
        return {"ticker": ticker, "overall_bullish_prob": round(bullish_prob, 2), "results": results}
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/tickers")
def get_available_tickers():
    dataset_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
    )
    print(f"🔍 Looking for dataset at: {os.path.abspath(dataset_path)}")
    if not os.path.exists(dataset_path):
        return JSONResponse({"error": "Dataset not found"}, status_code=404)
    try:
        df = pd.read_csv(dataset_path)
        tickers = sorted(df["ticker"].dropna().unique().tolist())
        return {"tickers": tickers}
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
