# ============================================================================
# FILE 3: modules/data_fetcher.py
# ============================================================================
# PURPOSE: This module fetches stock data from Yahoo Finance
#          - Searches for stock ticker symbols from company names
#          - Gets historical price data (OHLCV - Open, High, Low, Close, Volume)
#          - Retrieves company fundamental data
# ============================================================================

import yfinance as yf  # Yahoo Finance API
import pandas as pd    # Data manipulation
import requests        # HTTP requests for ticker search
from typing import Optional, Dict  # Type hints for better code
import streamlit as st  # For caching functionality
from datetime import datetime, timedelta

class StockDataFetcher:
    """
    A class to fetch stock market data.
    
    What it does:
    1. Searches for stock ticker symbols (e.g., "RELIANCE.NS")
    2. Gets historical price data (daily prices)
    3. Gets company information (P/E ratio, market cap, etc.)
    """
    
    def __init__(self):
        """
        Initialize the data fetcher.
        Creates an empty cache dictionary to store results.
        """
        self.cache = {}  # Store downloaded data to avoid repeat downloads
        print("✅ StockDataFetcher initialized")
    
    @st.cache_data(ttl=3600)  # Cache results for 1 hour (3600 seconds)
    def lookup_ticker(_self, company_name: str, region: str = 'IN') -> Optional[Dict]:
        """
        Search for stock ticker symbol using company name.
        
        EXAMPLE:
        Input: "Bank of Baroda"
        Output: {'symbol': 'BANKBARODA.NS', 'name': 'Bank of Baroda', ...}
        
        Args:
            company_name: Name of the company (e.g., "Reliance Industries")
            region: Market region - 'IN' for India, 'US' for USA
        
        Returns:
            Dictionary with stock information or None if not found
        """
        try:
            print(f"🔍 Searching for ticker: {company_name}")
            
            # Yahoo Finance search API endpoint
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            
            # Headers to mimic a web browser (some APIs require this)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Search parameters
            params = {
                'q': company_name,          # Search query
                'quotes_count': 5,          # Get top 5 results
                'newsCount': 0,             # Don't need news
                'enableFuzzyQuery': False,  # Exact matching
            }
            
            # Make the HTTP request
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()  # Convert response to Python dictionary
            
            # Check if we got results
            if 'quotes' in data and len(data['quotes']) > 0:
                quotes = data['quotes']
                
                # Filter by region (India or USA)
                if region == 'IN':
                    # Keep only Indian stocks (ending with .NS or .BO)
                    # .NS = National Stock Exchange (NSE)
                    # .BO = Bombay Stock Exchange (BSE)
                    quotes = [q for q in quotes if '.NS' in q.get('symbol', '') or '.BO' in q.get('symbol', '')]
                
                if quotes:
                    # Get the best matching result (first one)
                    best_match = quotes[0]
                    
                    result = {
                        'symbol': best_match.get('symbol'),      # e.g., "RELIANCE.NS"
                        'name': best_match.get('longname') or best_match.get('shortname'),  # Company name
                        'exchange': best_match.get('exchange'),  # e.g., "NSI" for NSE
                        'type': best_match.get('quoteType')      # e.g., "EQUITY"
                    }
                    
                    print(f"✅ Found: {result['symbol']}")
                    return result
            
            print("❌ No ticker found")
            return None
            
        except Exception as e:
            # If any error occurs, show error message and return None
            st.error(f"Ticker lookup error: {str(e)}")
            print(f"❌ Error: {e}")
            return None
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes (1800 seconds)
    def get_historical_data(_self, ticker: str, period: str = "1y", 
                           interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock price data.
        
        EXAMPLE:
        Input: ticker="RELIANCE.NS", period="1y"
        Output: DataFrame with columns: Open, High, Low, Close, Volume, Date
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
            period: Time period - '1mo', '3mo', '6mo', '1y', '5y'
            interval: Data interval - '1d' (daily), '1wk' (weekly), '1mo' (monthly)
        
        Returns:
            DataFrame with price data or None if error
        """
        try:
            print(f"📊 Fetching data for {ticker}...")
            
            # Create a yfinance Ticker object
            stock = yf.Ticker(ticker)
            
            # Download historical data
            data = stock.history(period=period, interval=interval)
            
            # Check if we got any data
            if data.empty:
                print(f"❌ No data available for {ticker}")
                return None
            
            # Standardize column names (capitalize first letter)
            # Original: 'open', 'high', 'low', 'close', 'volume'
            # After: 'Open', 'High', 'Low', 'Close', 'Volume'
            data.columns = [col.title() for col in data.columns]
            
            print(f"✅ Got {len(data)} days of data")
            return data
            
        except Exception as e:
            # Show error message if something goes wrong
            st.error(f"Data fetch error: {str(e)}")
            print(f"❌ Error: {e}")
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_fundamentals(_self, ticker: str) -> Optional[Dict]:
        """
        Fetch company fundamental data (financial metrics).
        
        EXAMPLE:
        Input: ticker="RELIANCE.NS"
        Output: {'Market Cap': 12000000000, 'P/E Ratio': 25.5, ...}
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with fundamental metrics or None if error
        """
        try:
            print(f"💼 Fetching fundamentals for {ticker}...")
            
            # Create yfinance Ticker object
            stock = yf.Ticker(ticker)
            
            # Get company information
            info = stock.info
            
            # Extract key fundamental metrics
            fundamentals = {
                'Market Cap': info.get('marketCap', 'N/A'),           # Total company value
                'P/E Ratio': info.get('trailingPE', 'N/A'),           # Price to Earnings ratio
                'P/B Ratio': info.get('priceToBook', 'N/A'),          # Price to Book ratio
                'Dividend Yield': info.get('dividendYield', 'N/A'),   # Dividend percentage
                'EPS': info.get('trailingEps', 'N/A'),                # Earnings per share
                'Beta': info.get('beta', 'N/A'),                      # Stock volatility
                '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'), # Highest price in 1 year
                '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),   # Lowest price in 1 year
                'Average Volume': info.get('averageVolume', 'N/A'),   # Avg daily trading volume
                'Sector': info.get('sector', 'N/A'),                  # Business sector
                'Industry': info.get('industry', 'N/A'),              # Specific industry
            }
            
            print(f"✅ Got fundamentals")
            return fundamentals
            
        except Exception as e:
            # If fundamentals not available, show warning
            st.warning(f"Fundamentals not available: {str(e)}")
            print(f"⚠️ Fundamentals unavailable: {e}")
            return None
    
    def get_company_info(_self, ticker: str) -> Optional[Dict]:
        """
        Get detailed company information.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with company details
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'website': info.get('website', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A')[:500]  # First 500 chars
            }
            
        except Exception as e:
            print(f"⚠️ Company info unavailable: {e}")
            return None


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.data_fetcher import StockDataFetcher
# 
# # Create fetcher object
# fetcher = StockDataFetcher()
# 
# # Search for ticker
# result = fetcher.lookup_ticker("Reliance Industries")
# print(result['symbol'])  # Output: "RELIANCE.NS"
# 
# # Get historical data
# data = fetcher.get_historical_data("RELIANCE.NS", period="1y")
# print(data.head())  # Shows first 5 rows
# 
# # Get fundamentals
# fundamentals = fetcher.get_fundamentals("RELIANCE.NS")
# print(fundamentals)
# 
# ============================================================================