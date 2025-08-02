from flask import Flask, request, jsonify
import os
from flask_cors import CORS

# Import your custom modules
from scraper import scrape_reviews
# IMPORTANT: Based on your previous sentiment_analyzer.py, you should import analyze_sentiment
# from that file directly, not from vaderSentiment.vaderSentiment
from sentiment_analyzer import analyze_sentiment # <- CORRECTED IMPORT

app = Flask(__name__)
# Configure CORS to allow all origins and methods
CORS(app, 
     origins=["*"],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True)

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"ERROR (app.py): {str(e)}")
    return jsonify({"status": "error", "message": "An unexpected error occurred. Please try again later."}), 500

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"message": "Welcome to the Product Review Sentiment Analyzer API! Use the /analyze_sentiment endpoint."})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/test', methods=['GET', 'OPTIONS'])
def test():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"status": "success", "message": "Backend is running!"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/analyze_sentiment', methods=['POST', 'OPTIONS'])
def get_sentiment():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    try:
        print("DEBUG (app.py): Received request for /analyze_sentiment endpoint.")
        data = request.get_json()
        
        if not data or 'url' not in data:
            print("ERROR (app.py): Invalid request. 'url' not provided in JSON body.")
            return jsonify({"error": "Please provide a 'url' in the request body."}), 400

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
            }), 500 # Internal Server Error, or 404 if URL truly invalid

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
            "insights_for_manager": sentiment_results.get("insights_for_manager"),
            # You might include detailed_sentiments for debugging or if the client wants it
            "detailed_sentiments": sentiment_results.get("detailed_sentiments") # <-- UNCOMMENTED THIS FOR YOU
        }

        print("DEBUG (app.py): Sentiment analysis complete. Sending JSON response.")
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

    except Exception as e:
        print(f"ERROR (app.py): {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred during sentiment analysis."}), 500

# Vercel serverless function handler
def handler(request):
    return app(request)

if __name__ == '__main__':
    # For local development:
    port = int(os.environ.get('PORT', 5000))
    print(f"DEBUG (app.py): Starting Flask app on host 0.0.0.0, port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
