"""
news.py — config.NEWS_RSS_FEEDS dagi manbalardan so'nggi yangiliklarni oladi.
Ta'limga oid bo'lgan-bo'lmaganini aniqlash content_generator.py dagi
Claude chaqiruvida amalga oshiriladi (bu yerda faqat xom ma'lumot yig'iladi).
"""

import feedparser

import config


def fetch_latest_headlines(limit_per_feed: int = 8) -> list:
    """
    Barcha RSS manbalardan so'nggi sarlavha/qisqacha mazmun/havolalarni yig'adi.
    Qaytaradi: [{"title": str, "summary": str, "link": str, "source": str}, ...]
    """
    items = []
    for feed_url in config.NEWS_RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            source_name = parsed.feed.get("title", feed_url)
            for entry in parsed.entries[:limit_per_feed]:
                items.append({
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get("summary", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "source": source_name,
                })
        except Exception:
            # Bitta manba ishlamay qolsa, qolganlari bilan davom etamiz
            continue
    return items
