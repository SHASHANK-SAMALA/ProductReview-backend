from flask import Flask, request, jsonify
import os
from flask_cors import CORS

# Import your custom modules
from scraper import scrape_reviews
from sentiment_analyzer import analyze_sentiment

app = Flask(__name__)
CORS(app, origins=["*"])

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"ERROR (app.py): {str(e)}")
    return jsonify({"status": "error", "message": "An unexpected error occurred. Please try again later."}), 500

@app.route('/')
def home():
    return "Welcome to the Product Review Sentiment Analyzer API! Use the /analyze_sentiment endpoint."

@app.route('/test')
def test():
    return jsonify({"status": "success", "message": "Backend is running!"})

@app.route('/analyze_sentiment', methods=['POST'])
def get_sentiment():
    try:
        print("DEBUG (app.py): Received request for /analyze_sentiment endpoint.")
        data = request.get_json()
        
        if not data or 'url' not in data:
            print("ERROR (app.py): Invalid request. 'url' not provided in JSON body.")
            return jsonify({"status": "error", "message": "Please provide a 'url' in the request body."}), 400

        product_url = data['url']
        print(f"DEBUG (app.py): Attempting to analyze URL: {product_url}")

        # Log the incoming request body for debugging
        print("DEBUG (app.py): Incoming request body:", data)

        # 1. Scrape Reviews using the scraper.py module
        try:
            print("DEBUG (app.py): Calling scrape_reviews function...")
            reviews = scrape_reviews(product_url)
        except Exception as e:
            print(f"ERROR (app.py): scrape_reviews failed with error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while scraping reviews. Please check the URL or try again later.",
                "error_details": str(e)
            }), 500

        if not reviews:
            print(f"ERROR (app.py): No reviews scraped from {product_url}.")
            return jsonify({
                "status": "error",
                "message": "Could not scrape reviews from the provided URL. Please check the URL or try again later. It might be a dynamic site or have anti-scraping measures.",
                "url": product_url
            }), 500

        print(f"DEBUG (app.py): Successfully scraped {len(reviews)} reviews. Proceeding to sentiment analysis.")

        # 2. Analyze Sentiment using your sentiment_analyzer.py module
        try:
            print("DEBUG (app.py): Calling analyze_sentiment function...")
            sentiment_results = analyze_sentiment(reviews)
        except Exception as e:
            print(f"ERROR (app.py): analyze_sentiment failed with error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred during sentiment analysis. Please try again later.",
                "error_details": str(e)
            }), 500

        # 3. Prepare Response for Client/Manager
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
            "insights_for_manager": sentiment_results.get("insights_for_manager", []),
            "detailed_sentiments": sentiment_results.get("detailed_sentiments", [])
        }

        print("DEBUG (app.py): Sentiment analysis complete. Sending JSON response.")
        print("DEBUG (app.py): Response data:", response_data)
        return jsonify(response_data), 200

    except Exception as e:
        print(f"ERROR (app.py): {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred during sentiment analysis."}), 500

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"DEBUG (app.py): Starting Flask app on host 0.0.0.0, port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)