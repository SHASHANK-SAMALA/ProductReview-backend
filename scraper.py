# scraper.py
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# You can expand this list with any UA strings you like
HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]

# Common review-related CSS selectors / attributes
REVIEW_SELECTORS = [
    '[itemtype="http://schema.org/Review"]',
    '[itemprop="reviewBody"]',
    '.review',
    '.reviews',
    '[data-review]',
    '[class*="review"]',
    '[id*="review"]',
]

# Fallback keywords to sniff out “review-like” paragraphs
REVIEW_KEYWORDS = [
    "good", "bad", "excellent", "poor",
    "worst", "nice", "awesome", "terrible",
    "satisfied", "unsatisfied", "recommend",
    "disappointed", "love", "hate",
]

def scrape_reviews(url: str, max_reviews: int = 6000) -> list[str]:
    """
    Enhanced review scraper to handle large datasets.
    Returns up to `max_reviews` review texts from any site.
    """
    # —— Setup headless Chrome —— #
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    ua = random.choice(HEADERS_LIST)
    options.add_argument(f"user-agent={ua}")

    driver = webdriver.Chrome(options=options)
    reviews = []

    try:
        driver.get(url)
        time.sleep(3)  # allow JS to load

        # Scroll to bottom multiple times to load more reviews
        for i in range(10):  # Adjust the number of scrolls based on site behavior
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"DEBUG: Scroll iteration {i+1} completed.")

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract reviews using structured selectors
        for sel in REVIEW_SELECTORS:
            for el in soup.select(sel):
                text = el.get_text(" ", strip=True)
                if len(text) > 30:
                    reviews.append(text)
                    if len(reviews) >= max_reviews:
                        break
            if reviews:
                break

        # Fallback: Extract review-like content
        if not reviews:
            for tag in soup.find_all(["p", "span"]):
                txt = tag.get_text(" ", strip=True)
                low = txt.lower()
                if len(txt) > 40 and any(kw in low for kw in REVIEW_KEYWORDS):
                    reviews.append(txt)
                    if len(reviews) >= max_reviews:
                        break

    except Exception as e:
        print(f"[scraper.py] ERROR during scrape: {e}")
    finally:
        driver.quit()

    # Deduplicate reviews
    unique_reviews = list(dict.fromkeys(reviews))
    print(f"DEBUG: Total unique reviews extracted: {len(unique_reviews)}")
    return unique_reviews[:max_reviews]
