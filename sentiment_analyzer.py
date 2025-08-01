from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Initialize the VADER sentiment analyzer globally or once per run for efficiency
analyzer = SentimentIntensityAnalyzer()

def preprocess_text(text):
    """
    Cleans the review text for sentiment analysis.
    VADER is somewhat robust to capitalization and punctuation, so light preprocessing is applied.
    """
    # Remove HTML tags (if any slipped through scraping)
    text = re.sub(r'<.*?>', '', text)
    # Remove extra spaces (important for clean text)
    text = re.sub(r'\s+', ' ', text).strip()
    # VADER is designed to handle punctuation, capitalization, and emojis,
    # so we don't convert to lowercase or remove most punctuation here.
    return text

def analyze_sentiment(reviews):
    """
    Enhanced sentiment analysis for large datasets.
    Returns overall sentiment statistics, top reviews, and actionable insights.
    """
    print("DEBUG: Starting sentiment analysis with VADER.")
    if not reviews:
        print("DEBUG: No reviews provided for sentiment analysis.")
        return {
            "overall_sentiment": "No reviews to analyze.",
            "total_reviews": 0,
            "positive_percentage": 0,
            "negative_percentage": 0,
            "neutral_percentage": 0,
            "top_positive_reviews": [],
            "top_negative_reviews": [],
            "insights_for_manager": ["No data available to generate insights."],
            "detailed_sentiments": []
        }

    total_reviews = len(reviews)
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    sentiments = []

    for review in reviews:
        processed_review = preprocess_text(review)
        vs = analyzer.polarity_scores(processed_review)

        # Debugging sentiment scores
        print(f"DEBUG: Review: {processed_review}")
        print(f"DEBUG: Sentiment Scores: {vs}")

        sentiment = 'neutral'
        if vs['compound'] > 0.1:  # Adjusted threshold for positive
            sentiment = 'positive'
            positive_count += 1
        elif vs['compound'] < -0.1:  # Adjusted threshold for negative
            sentiment = 'negative'
            negative_count += 1
        else:
            neutral_count += 1

        sentiments.append({
            "original_review": review,
            "processed_review": processed_review,
            "sentiment": sentiment,
            "vader_scores": vs
        })

    positive_reviews = sorted([s for s in sentiments if s['sentiment'] == 'positive'], key=lambda x: x['vader_scores']['compound'], reverse=True)
    negative_reviews = sorted([s for s in sentiments if s['sentiment'] == 'negative'], key=lambda x: x['vader_scores']['compound'])

    positive_percentage = (positive_count / total_reviews) * 100
    negative_percentage = (negative_count / total_reviews) * 100
    neutral_percentage = (neutral_count / total_reviews) * 100

    overall_sentiment = "Neutral"
    if positive_percentage > (negative_percentage + neutral_percentage * 0.5):
        overall_sentiment = "Positive"
    elif negative_percentage > (positive_percentage + neutral_percentage * 0.5):
        overall_sentiment = "Negative"

    insights = generate_insights(sentiments, overall_sentiment)

    print(f"DEBUG: Sentiment Summary - Positive: {positive_percentage:.2f}%, Negative: {negative_percentage:.2f}%, Neutral: {neutral_percentage:.2f}%")

    return {
        "overall_sentiment": overall_sentiment,
        "total_reviews": total_reviews,
        "positive_percentage": round(positive_percentage, 2),
        "negative_percentage": round(negative_percentage, 2),
        "neutral_percentage": round(neutral_percentage, 2),
        "top_positive_reviews": positive_reviews[:5],
        "top_negative_reviews": negative_reviews[:5],
        "insights_for_manager": insights,
        "detailed_sentiments": sentiments
    }

def generate_insights(sentiments_data, overall_sentiment):
    """
    Generates exactly 5 key insights for a manager based on sentiment analysis results.
    """
    insights = []
    print(f"DEBUG: Generating insights for overall sentiment: {overall_sentiment}")
    
    # Define common words to exclude for more meaningful feature extraction
    common_positive_words = {"great", "good", "love", "excellent", "best", "product", "very", "would", "really", "much", "well", "amazing", "highly", "recommend", "happy", "perfectly", "quick"}
    common_negative_words = {"bad", "poor", "issue", "problem", "not", "disappointed", "worst", "product", "very", "would", "really", "much", "well", "terrible", "waste", "away", "buggy", "crashes"}

    # Calculate statistics
    total_reviews = len(sentiments_data)
    positive_reviews = [s for s in sentiments_data if s['sentiment'] == 'positive']
    negative_reviews = [s for s in sentiments_data if s['sentiment'] == 'negative']
    neutral_reviews = [s for s in sentiments_data if s['sentiment'] == 'neutral']
    
    positive_count = len(positive_reviews)
    negative_count = len(negative_reviews)
    neutral_count = len(neutral_reviews)
    
    positive_percentage = (positive_count / total_reviews * 100) if total_reviews > 0 else 0
    negative_percentage = (negative_count / total_reviews * 100) if total_reviews > 0 else 0
    neutral_percentage = (neutral_count / total_reviews * 100) if total_reviews > 0 else 0

    # Insight 1: Overall Product Sentiment
    if overall_sentiment == "Positive":
        insights.append(f"Product is generally well-received with {positive_percentage:.1f}% positive reviews. Customers are satisfied with the product quality and performance.")
    elif overall_sentiment == "Negative":
        insights.append(f"Product has significant issues with {negative_percentage:.1f}% negative reviews. Immediate attention required to address customer concerns.")
    else:
        insights.append(f"Product has mixed reviews with {positive_percentage:.1f}% positive, {negative_percentage:.1f}% negative, and {neutral_percentage:.1f}% neutral feedback.")

    # Insight 2: Key Features Mentioned
    positive_reviews_text = [s['processed_review'] for s in positive_reviews]
    if positive_reviews_text:
        common_words = {}
        for review in positive_reviews_text:
            words = re.findall(r'\b\w+\b', review.lower())
            for word in words:
                if len(word) > 3 and word not in common_positive_words:
                    common_words[word] = common_words.get(word, 0) + 1
        
        if common_words:
            top_features = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:3]
            feature_names = [word.capitalize() for word, count in top_features]
            insights.append(f"Key positive features mentioned: {', '.join(feature_names)}. These are the main selling points customers appreciate.")
        else:
            insights.append("No specific features were frequently mentioned in positive reviews.")
    else:
        insights.append("No positive reviews to extract key features from.")

    # Insight 3: Issues/Problems
    negative_reviews_text = [s['processed_review'] for s in negative_reviews]
    if negative_reviews_text:
        common_words = {}
        for review in negative_reviews_text:
            words = re.findall(r'\b\w+\b', review.lower())
            for word in words:
                if len(word) > 3 and word not in common_negative_words:
                    common_words[word] = common_words.get(word, 0) + 1
        
        if common_words:
            top_issues = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:3]
            issue_names = [word.capitalize() for word, count in top_issues]
            insights.append(f"Main issues reported: {', '.join(issue_names)}. These problems need immediate attention and improvement.")
        else:
            insights.append("No specific issues were frequently mentioned in negative reviews.")
    else:
        insights.append("No negative reviews to extract issues from.")

    # Insight 4: Purchase/Recommendation Insights
    recommendation_keywords = ["recommend", "buy", "purchase", "worth", "value", "money", "price", "cost"]
    recommendation_reviews = []
    
    for review in sentiments_data:
        review_lower = review['processed_review'].lower()
        if any(keyword in review_lower for keyword in recommendation_keywords):
            recommendation_reviews.append(review)
    
    if recommendation_reviews:
        positive_recs = [r for r in recommendation_reviews if r['sentiment'] == 'positive']
        negative_recs = [r for r in recommendation_reviews if r['sentiment'] == 'negative']
        
        if positive_recs and negative_recs:
            insights.append(f"Purchase recommendations: {len(positive_recs)} customers would recommend buying, {len(negative_recs)} would not recommend.")
        elif positive_recs:
            insights.append(f"Purchase recommendations: {len(positive_recs)} customers would recommend buying this product.")
        elif negative_recs:
            insights.append(f"Purchase recommendations: {len(negative_recs)} customers would not recommend buying this product.")
        else:
            insights.append("Limited purchase recommendation data available in reviews.")
    else:
        insights.append("No specific purchase or recommendation mentions found in reviews.")

    # Insight 5: Overall Review Summary
    if total_reviews > 0:
        if positive_percentage > 70:
            insights.append(f"Overall: Excellent product with {positive_count} out of {total_reviews} customers giving positive feedback. Strong market position.")
        elif positive_percentage > 50:
            insights.append(f"Overall: Good product with {positive_count} out of {total_reviews} customers satisfied. Room for improvement.")
        elif negative_percentage > 50:
            insights.append(f"Overall: Poor product with {negative_count} out of {total_reviews} customers dissatisfied. Needs major improvements.")
        else:
            insights.append(f"Overall: Mixed product with {positive_count} positive, {negative_count} negative, and {neutral_count} neutral reviews out of {total_reviews} total.")
    else:
        insights.append("Overall: No reviews available for analysis.")

    return insights[:5]  # Ensure exactly 5 insights

# Example Usage for testing this specific module - now without hardcoded reviews for primary logic
if __name__ == '__main__':
    print("\n--- Testing VADER Sentiment Analyzer Module ---")
    print("This block demonstrates how to use the analyzer.")
    print("In a full application, reviews would come from the scraper.")

    # Placeholder for scraped reviews - in a real scenario, this would be `scraped_data`
    # from your scraper.py
    # For testing this module directly, you could temporarily put some reviews here:
    
    # For a quick test, you can uncomment this temporary list:
    temp_reviews_for_isolated_test = [
        "This product is truly wonderful! I couldn't be happier. 👍",
        "It was okay, not great, not terrible.",
        "Absolutely awful! A complete rip-off. 😠",
        "Pretty good value for money, but delivery was slow.",
        "Indifferent. It just works.",
        "What a fantastic device! Battery life is superb.",
        "Broken on arrival. Very frustrating experience.",
        "Decent, but the user interface is confusing."
    ]
    
    # If you're running this file directly, use the temp_reviews for demonstration
    # Otherwise, in the integrated script, you'd pass the actual scraped reviews.
    
    if 'temp_reviews_for_isolated_test' in locals() and temp_reviews_for_isolated_test:
        print(f"\nDEBUG: Using {len(temp_reviews_for_isolated_test)} temporary reviews for isolated module testing.")
        results = analyze_sentiment(temp_reviews_for_isolated_test)
        
        print("\n--- Sentiment Analysis Results Summary ---")
        for k, v in results.items():
            if k not in ["detailed_sentiments", "insights_for_manager"]:
                print(f"{k}: {v}")
        
        print("\nInsights for Manager:")
        for insight in results["insights_for_manager"]:
            print(f"- {insight}")

        print("\nDetailed sentiments (first 3 reviews and last 1 for brevity):")
        for i, s in enumerate(results["detailed_sentiments"]):
            if i < 3 or i == len(results["detailed_sentiments"]) - 1:
                print(f"  Original: '{s['original_review'][:70]}...'")
                print(f"  Processed: '{s['processed_review'][:70]}...'")
                print(f"    Sentiment: {s['sentiment']}, VADER Scores: {s['vader_scores']}")
    else:
        print("\nTo test this module directly, provide a list of reviews (e.g., uncomment `temp_reviews_for_isolated_test`).")
        print("In an integrated application, this function will receive reviews from your scraper.")
    
    print("\n--- VADER Sentiment Analyzer Module Test Complete ---")