from flask import Flask, request, jsonify
import os
from flask_cors import CORS

# Custom modules
from scraper import scrape_reviews
from sentiment_analyzer import analyze_sentiment

app = Flask(__name__)

# ✅ Correct and secure CORS configuration
CORS(app,
     origins=[
         "http://localhost:5173",  # Dev
         "https://opinionpulse.vercel.app",  # Vercel Prod 1
         "https://product-review-frontend-two.vercel.app"  # Vercel Prod 2
     ],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True)

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"ERROR (app.py): {str(e)}")
    return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the Product Review Sentiment Analyzer API. Use the /analyze_sentiment endpoint."
    })

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "Backend is running!"})

@app.route('/analyze_sentiment', methods=['POST'])
def get_sentiment():
    try:
        print("DEBUG: /analyze_sentiment request received.")
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({"error": "Missing 'url' in request body."}), 400

        product_url = data['url']
        print(f"DEBUG: Scraping reviews from URL: {product_url}")
        reviews = scrape_reviews(product_url)

        if not reviews:
            return jsonify({
                "status": "error",
                "message": "No reviews found. The page may block scraping or contain no reviews."
            }), 404

        print(f"DEBUG: Analyzing {len(reviews)} reviews.")
        sentiment_results = analyze_sentiment(reviews)

        response_data = {
            "status": "success",
            "url": product_url,
            "summary": {
                "total_reviews_found": sentiment_results.get("total_reviews", 0),
                "overall_sentiment": sentiment_results.get("overall_sentiment"),
                "positive_percentage": sentiment_results.get("positive_percentage"),
                "negative_percentage": sentiment_results.get("negative_percentage"),
                "neutral_percentage": sentiment_results.get("neutral_percentage")
            },
            "insights_for_manager": sentiment_results.get("insights_for_manager"),
            "detailed_sentiments": sentiment_results.get("detailed_sentiments")
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"ERROR in /analyze_sentiment: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error."}), 500

# For Render deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
