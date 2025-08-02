import requests
from bs4 import BeautifulSoup
import random

SCRAPER_API_KEY = "2276d9f31fc2af6450c024e1e1315066" # Replace with real key

HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]

REVIEW_KEYWORDS = [
    "good", "bad", "excellent", "poor", "worst", "nice", "awesome", "terrible",
    "satisfied", "unsatisfied", "recommend", "disappointed", "love", "hate"
]

def scrape_reviews(url: str, max_reviews: int = 500) -> list[str]:
    try:
        print(f"🔍 [scraper.py] Fetching: {url}")

        api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&render=true"
        headers = {
            "User-Agent": random.choice(HEADERS_LIST)
        }

        resp = requests.get(api_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"❌ Fetch failed: Status {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")
        reviews = []

        for tag in soup.find_all(["p", "span", "div"]):
            txt = tag.get_text(" ", strip=True)
            low = txt.lower()
            if len(txt) > 40 and any(kw in low for kw in REVIEW_KEYWORDS):
                reviews.append(txt)
                if len(reviews) >= max_reviews:
                    break

        unique_reviews = list(dict.fromkeys(reviews))
        print(f"✅ [scraper.py] Reviews scraped: {len(unique_reviews)}")
        return unique_reviews

    except Exception as e:
        print(f"❌ [scraper.py] Error: {e}")
        return []
