"""
Sentiment Analyzer Module with GoogleNews
"""

import sys
import os
from datetime import datetime, timedelta

# Force add paths
sys.path.insert(0, '/usr/local/python/3.12.1/lib/python3.12/site-packages')
sys.path.insert(0, '/home/codespace/.local/lib/python3.12/site-packages')

try:
    from googlenews import GoogleNews
    print("✅ GoogleNews imported successfully")
except ImportError as e:
    print(f"⚠️ GoogleNews import failed: {e}")
    GoogleNews = None

import streamlit as st


class SentimentAnalyzer:
    """Analyzes news sentiment for stocks using GoogleNews"""
    
    def __init__(self):
        print("✅ SentimentAnalyzer initialized")
        self.positive_words = [
            'profit', 'gain', 'up', 'rise', 'high', 'growth', 'success',
            'positive', 'strong', 'beat', 'surge', 'rally', 'boost', 'advance'
        ]
        self.negative_words = [
            'loss', 'down', 'fall', 'decline', 'drop', 'negative', 'weak',
            'miss', 'crash', 'plunge', 'concern', 'risk', 'cut', 'lower'
        ]
    
    @st.cache_data(ttl=1800)
    def get_stock_news(_self, company_name: str, days_back: int = 30) -> list:
        """Fetch recent news articles"""
        try:
            print(f"📰 Fetching news for {company_name}...")
            
            if GoogleNews is None:
                print("⚠️ GoogleNews not available, using sample data")
                return _self._get_sample_news(company_name)
            
            googlenews = GoogleNews(lang='en', region='IN')
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now()
            
            googlenews.set_time_range(
                start_date.strftime('%m/%d/%Y'),
                end_date.strftime('%m/%d/%Y')
            )
            googlenews.search(company_name + ' stock')
            results = googlenews.results()
            
            news_list = []
            for article in results[:20]:
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
            return _self._get_sample_news(company_name)
    
    def _get_sample_news(_self, company_name: str) -> list:
        """Fallback sample news"""
        return [
            {
                'title': f'{company_name} shows strong performance',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Financial News',
                'link': '#'
            },
            {
                'title': f'{company_name} reports quarterly earnings',
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'source': 'Reuters',
                'link': '#'
            }
        ]
    
    def analyze_sentiment(self, news_list: list) -> float:
        """Analyze sentiment of news articles"""
        if not news_list:
            return 0.5
        
        try:
            print("🤔 Analyzing sentiment...")
            positive_count = 0
            negative_count = 0
            
            for article in news_list:
                title = article.get('title', '').lower()
                
                for word in self.positive_words:
                    if word in title:
                        positive_count += 1
                
                for word in self.negative_words:
                    if word in title:
                        negative_count += 1
            
            if positive_count + negative_count == 0:
                sentiment_score = 0.5
            else:
                sentiment_score = positive_count / (positive_count + negative_count)
            
            for article in news_list:
                title = article.get('title', '').lower()
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
            print(f"❌ Error: {e}")
            return 0.5
