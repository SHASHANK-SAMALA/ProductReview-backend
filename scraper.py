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
    '.customer-review',
    '.product-review',
    '.user-review',
    '.comment',
    '.feedback',
    '.testimonial',
]

# Fallback keywords to sniff out "review-like" paragraphs
REVIEW_KEYWORDS = [
    "good", "bad", "excellent", "poor",
    "worst", "nice", "awesome", "terrible",
    "satisfied", "unsatisfied", "recommend",
    "disappointed", "love", "hate",
    "great", "amazing", "horrible", "perfect",
    "quality", "worth", "value", "price",
    "delivery", "service", "product", "item"
]

def scrape_reviews(url: str, max_reviews: int = 6000) -> list[str]:
    """
    Enhanced review scraper to handle large datasets.
    Returns up to `max_reviews` review texts from any site.
    """
    print(f"DEBUG: Starting to scrape reviews from: {url}")
    
    # —— Setup headless Chrome —— #
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    ua = random.choice(HEADERS_LIST)
    options.add_argument(f"user-agent={ua}")

    driver = None
    reviews = []

    try:
        print("DEBUG: Initializing Chrome driver...")
        driver = webdriver.Chrome(options=options)
        
        print("DEBUG: Navigating to URL...")
        driver.get(url)
        time.sleep(5)  # allow JS to load

        print("DEBUG: Starting to scroll to load more content...")
        # Scroll to bottom multiple times to load more reviews
        for i in range(5):  # Reduced scrolls for faster processing
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"DEBUG: Scroll iteration {i+1} completed.")

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        print("DEBUG: Extracting reviews using structured selectors...")
        # Extract reviews using structured selectors
        for sel in REVIEW_SELECTORS:
            elements = soup.select(sel)
            print(f"DEBUG: Found {len(elements)} elements with selector: {sel}")
            for el in elements:
                text = el.get_text(" ", strip=True)
                if len(text) > 30:
                    reviews.append(text)
                    if len(reviews) >= max_reviews:
                        break
            if len(reviews) >= max_reviews:
                break

        # Fallback: Extract review-like content
        if not reviews:
            print("DEBUG: No reviews found with structured selectors, trying fallback method...")
            for tag in soup.find_all(["p", "span", "div"]):
                txt = tag.get_text(" ", strip=True)
                low = txt.lower()
                if len(txt) > 40 and any(kw in low for kw in REVIEW_KEYWORDS):
                    reviews.append(txt)
                    if len(reviews) >= max_reviews:
                        break

        print(f"DEBUG: Total reviews extracted: {len(reviews)}")

    except Exception as e:
        print(f"[scraper.py] ERROR during scrape: {e}")
        raise e
    finally:
        if driver:
            driver.quit()
            print("DEBUG: Chrome driver closed.")

    # Deduplicate reviews
    unique_reviews = list(dict.fromkeys(reviews))
    print(f"DEBUG: Total unique reviews extracted: {len(unique_reviews)}")
    
    if not unique_reviews:
        print("DEBUG: No reviews found. This might be due to:")
        print("1. The URL doesn't contain review content")
        print("2. The site uses dynamic loading that requires more time")
        print("3. The site has anti-scraping measures")
        print("4. The selectors need to be updated for this specific site")
    
    return unique_reviews[:max_reviews]
