import feedparser
from typing import List, Dict

def get_finance_news(symbol: str = "^GSPC") -> List[Dict[str, str]]:
    try:
        feed = feedparser.parse(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}")
        return [{
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "")
        } for entry in feed.entries[:5]]
    except Exception:
        return [{"title": "News feed unavailable", "link": "#"}]