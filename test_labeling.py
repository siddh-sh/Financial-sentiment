from utils.api_clients import fetch_alpha_daily
from utils.labeling import label_news_item

prices = fetch_alpha_daily("AAPL")
print("Fetched days:", len(prices))
if prices:
    sample_date = list(prices.keys())[10]
    print("Sample date:", sample_date)
    print("Label:", label_news_item(sample_date, prices))
else:
    print("No price data fetched. Check your Alpha Vantage key.")
