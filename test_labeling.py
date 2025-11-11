from utils.labeling import label_news_item

prices_example = {
    "2025-11-06": 142.10,
    "2025-11-07": 143.55
}

print(label_news_item("2025-11-06", prices_example))
