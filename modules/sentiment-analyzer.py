# ============================================================================
# FILE 5: modules/sentiment_analyzer.py (SIMPLIFIED VERSION)
# ============================================================================
# PURPOSE: Analyze news sentiment for stocks
#          - Fetch news articles
#          - Analyze sentiment (positive/negative/neutral)
#          - Calculate overall sentiment score
# ============================================================================

from googlenews import GoogleNews
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


class SentimentAnalyzer:
    """
    A class to analyze news sentiment.
    
    What it does:
    1. Fetches recent news articles about a stock
    2. Analyzes sentiment (simplified version - uses keywords)
    3. Returns sentiment score (0 to 1, where 1 = very positive)
    
    NOTE: This is a simplified version without FinBERT
    For production, you can add transformers/FinBERT later
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        print("✅ SentimentAnalyzer initialized")
        
        # Positive and negative keywords for simple sentiment analysis
        self.positive_words = [
            'profit', 'gain', 'up', 'rise', 'high', 'growth', 'success',
            'positive', 'strong', 'beat', 'surge', 'rally', 'boost', 'advance'
        ]
        
        self.negative_words = [
            'loss', 'down', 'fall', 'decline', 'drop', 'negative', 'weak',
            'miss', 'crash', 'plunge', 'concern', 'risk', 'cut', 'lower'
        ]
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_stock_news(_self, company_name: str, days_back: int = 30) -> list:
        """
        Fetch recent news articles about a stock.
        
        EXAMPLE:
        Input: company_name="Reliance", days_back=30
        Output: [{'title': '...', 'date': '...', 'source': '...'}, ...]
        
        Args:
            company_name: Name of the company
            days_back: How many days of news to fetch
        
        Returns:
            List of news articles (dictionaries)
        """
        try:
            print(f"📰 Fetching news for {company_name}...")
            
            # Initialize Google News
            googlenews = GoogleNews(lang='en', region='IN')
            
            # Set time period
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now()
            googlenews.set_time_range(start_date.strftime('%m/%d/%Y'), 
                                     end_date.strftime('%m/%d/%Y'))
            
            # Search for news
            googlenews.search(company_name + ' stock')
            
            # Get results
            results = googlenews.results()
            
            # Format news articles
            news_list = []
            for article in results[:20]:  # Get top 20 articles
                news_list.append({
                    'title': article.get('title', 'No title'),
                    'date': article.get('date', 'Unknown'),
                    'source': article.get('media', 'Unknown'),
                    'link': article.get('link', '#')
                })
            
            print(f"✅ Found {len(news_list)} articles")
            return news_list
            
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            st.warning("Could not fetch news. Using neutral sentiment.")
            return []
    
    def analyze_sentiment(self, news_list: list) -> float:
        """
        Analyze sentiment of news articles (simplified keyword-based).
        
        EXAMPLE:
        Input: news_list with titles containing "profit surge"
        Output: 0.75 (positive sentiment)
        
        Args:
            news_list: List of news articles
        
        Returns:
            Sentiment score (0.0 to 1.0)
            - 0.0 to 0.3 = Very Negative
            - 0.3 to 0.5 = Negative
            - 0.5 = Neutral
            - 0.5 to 0.7 = Positive
            - 0.7 to 1.0 = Very Positive
        """
        if not news_list:
            print("ℹ️ No news available, returning neutral sentiment")
            return 0.5  # Neutral
        
        try:
            print("🤔 Analyzing sentiment...")
            
            positive_count = 0
            negative_count = 0
            total_articles = len(news_list)
            
            # Analyze each article
            for article in news_list:
                title = article.get('title', '').lower()
                
                # Count positive words
                for word in self.positive_words:
                    if word in title:
                        positive_count += 1
                
                # Count negative words
                for word in self.negative_words:
                    if word in title:
                        negative_count += 1
            
            # Calculate sentiment score
            if positive_count + negative_count == 0:
                sentiment_score = 0.5  # Neutral if no keywords found
            else:
                # Score between 0 and 1
                sentiment_score = positive_count / (positive_count + negative_count)
            
            # Add news to articles for display
            for i, article in enumerate(news_list):
                title = article.get('title', '').lower()
                
                # Determine sentiment for this article
                pos = sum(1 for w in self.positive_words if w in title)
                neg = sum(1 for w in self.negative_words if w in title)
                
                if pos > neg:
                    article['sentiment'] = 'Positive 😊'
                elif neg > pos:
                    article['sentiment'] = 'Negative 😟'
                else:
                    article['sentiment'] = 'Neutral 😐'
            
            print(f"✅ Sentiment score: {sentiment_score:.2f}")
            return sentiment_score
            
        except Exception as e:
            print(f"❌ Error analyzing sentiment: {e}")
            return 0.5  # Return neutral on error


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.sentiment_analyzer import SentimentAnalyzer
# 
# # Create analyzer
# analyzer = SentimentAnalyzer()
# 
# # Get news
# news = analyzer.get_stock_news("Reliance")
# 
# # Analyze sentiment
# score = analyzer.analyze_sentiment(news)
# 
# if score > 0.6:
#     print("Positive news! 😊")
# elif score < 0.4:
#     print("Negative news! 😟")
# else:
#     print("Neutral news 😐")
# 
# ============================================================================