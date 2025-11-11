from datetime import datetime, timedelta

def label_news_item(news_date_str: str, prices: dict):
    """
    news_date_str: 'YYYY-MM-DD'
    prices: dict { 'YYYY-MM-DD': close_price_float }
    returns 1 (bullish) / 0 (bearish) / None if not possible
    """

    # convert to date object
    try:
        news_date = datetime.fromisoformat(news_date_str).date()
    except:
        return None

    # find base trading day (today or previous valid)
    base_date = news_date
    attempts = 0
    while attempts < 7:  # max 1 week back
        d_str = base_date.isoformat()
        if d_str in prices:
            break
        base_date = base_date - timedelta(days=1)
        attempts += 1
    else:
        return None

    today_close = prices.get(base_date.isoformat())
    if today_close is None:
        return None

    # find next trading day
    next_date = base_date + timedelta(days=1)
    attempts = 0
    while attempts < 7:
        d_str = next_date.isoformat()
        if d_str in prices:
            break
        next_date = next_date + timedelta(days=1)
        attempts += 1
    else:
        return None

    next_close = prices.get(next_date.isoformat())
    if next_close is None:
        return None

    # bullish or bearish
    return 1 if next_close > today_close else 0
