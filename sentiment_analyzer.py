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
"insights_for_manager": insights[:5],
        "detailed_sentiments": sentiments
    }

def generate_insights(sentiments_data, overall_sentiment):
    """
    Generates exactly 5 actionable insights for a manager based on sentiment analysis results.
    """
    insights = []
    total_reviews = len(sentiments_data)
    positive_count = len([s for s in sentiments_data if s['sentiment'] == 'positive'])
    negative_count = len([s for s in sentiments_data if s['sentiment'] == 'negative'])
    neutral_count = len([s for s in sentiments_data if s['sentiment'] == 'neutral'])
    
    positive_percentage = (positive_count / total_reviews) * 100 if total_reviews > 0 else 0
    negative_percentage = (negative_count / total_reviews) * 100 if total_reviews > 0 else 0
    
    print(f"DEBUG: Generating insights for overall sentiment: {overall_sentiment}")
    
    # Define common words to exclude for more meaningful feature extraction
    common_positive_words = {"great", "good", "love", "excellent", "best", "product", "very", "would", "really", "much", "well", "amazing", "highly", "recommend", "happy", "perfectly", "quick"}
    common_negative_words = {"bad", "poor", "issue", "problem", "not", "disappointed", "worst", "product", "very", "would", "really", "much", "well", "terrible", "waste", "away", "buggy", "crashes"}

    # Insight 1: Overall sentiment assessment
    if overall_sentiment == "Positive":
        insights.append(f"Overall Customer Satisfaction: {positive_percentage:.1f}% of reviews are positive, indicating strong customer satisfaction with this product.")
    elif overall_sentiment == "Negative":
        insights.append(f"Critical Issues Detected: {negative_percentage:.1f}% of reviews are negative, requiring immediate attention to address customer concerns.")
    else:
        insights.append(f"Mixed Reception: Reviews are balanced with {positive_percentage:.1f}% positive and {negative_percentage:.1f}% negative, suggesting room for improvement.")
    
    # Insight 2: Review volume and engagement
    if total_reviews >= 50:
        insights.append(f"High Engagement: With {total_reviews} reviews analyzed, this product has strong customer engagement and market presence.")
    elif total_reviews >= 20:
        insights.append(f"Moderate Engagement: {total_reviews} reviews indicate decent customer interaction, but more feedback could provide better insights.")
    else:
        insights.append(f"Limited Feedback: Only {total_reviews} reviews available. Consider strategies to encourage more customer reviews for comprehensive analysis.")
    
    # Insight 3: Positive feature analysis
    positive_reviews_text = [s['processed_review'] for s in sentiments_data if s['sentiment'] == 'positive']
    if positive_reviews_text:
        common_words = {}
        for review in positive_reviews_text:
            words = re.findall(r'\b\w+\b', review.lower())
            for word in words:
                if len(word) > 3 and word not in common_positive_words:
                    common_words[word] = common_words.get(word, 0) + 1
        
        sorted_common_words = sorted(common_words.items(), key=lambda item: item[1], reverse=True)
        if sorted_common_words[:3]:
            top_features = [word for word, count in sorted_common_words[:3]]
            insights.append(f"Key Strengths: Customers frequently praise '{', '.join(top_features)}'. Leverage these strengths in marketing and product positioning.")
        else:
            insights.append("Positive Feedback: Customers express satisfaction, though specific features aren't clearly highlighted in reviews.")
    else:
        insights.append("Limited Positive Feedback: Few positive reviews available. Focus on understanding what customers value most.")
    
    # Insight 4: Areas for improvement
    negative_reviews_text = [s['processed_review'] for s in sentiments_data if s['sentiment'] == 'negative']
    if negative_reviews_text:
        common_words = {}
        for review in negative_reviews_text:
            words = re.findall(r'\b\w+\b', review.lower())
            for word in words:
                if len(word) > 3 and word not in common_negative_words:
                    common_words[word] = common_words.get(word, 0) + 1
        
        sorted_common_words = sorted(common_words.items(), key=lambda item: item[1], reverse=True)
        if sorted_common_words[:3]:
            top_issues = [word for word, count in sorted_common_words[:3]]
            insights.append(f"Improvement Areas: Common concerns include '{', '.join(top_issues)}'. Address these issues to reduce negative feedback.")
        else:
            insights.append("Negative Feedback: Some dissatisfaction exists, but specific issues aren't clearly identifiable from review text.")
    else:
        insights.append("Minimal Complaints: Very few negative reviews suggest the product meets most customer expectations.")
    
    # Insight 5: Strategic recommendations
    if positive_percentage > 70:
        insights.append("Strategic Recommendation: Strong positive sentiment suggests this product is market-ready for expansion and premium positioning.")
    elif negative_percentage > 50:
        insights.append("Strategic Recommendation: High negative sentiment requires immediate product review, quality improvements, or customer service enhancement.")
    elif neutral_count > total_reviews * 0.4:
        insights.append("Strategic Recommendation: High neutral sentiment indicates customers are indifferent. Consider adding unique features or value propositions.")
    else:
        insights.append("Strategic Recommendation: Balanced feedback suggests steady performance. Monitor trends and gather targeted feedback for optimization.")
    
    # Ensure exactly 5 insights
    while len(insights) < 5:
        insights.append("Additional Analysis: More comprehensive data collection recommended for deeper insights into customer preferences and market positioning.")
    
    return insights[:5]

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