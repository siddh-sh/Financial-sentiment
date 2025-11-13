from datetime import datetime, timedelta

def label_news_item(date_str, prices):
    """
    Given an article date (YYYY-MM-DD) and dict of prices {date: close},
    return label:
      1 → bullish (next-day close > same-day close)
      0 → bearish
      None → if next-day price not available
    """
    try:
        # normalize date format
        date_obj = datetime.fromisoformat(date_str[:10])
        today = date_obj.strftime("%Y-%m-%d")
        next_day = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

        if today in prices and next_day in prices:
            return 1 if prices[next_day] > prices[today] else 0
        else:
            return None
    except Exception:
        return None
