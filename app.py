"""
Advanced Stock Analysis & Prediction System
============================================
Main Streamlit Application

HOW TO RUN: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Import custom modules
from modules.data-fetcher import StockDataFetcher
from modules.technical-analysis import TechnicalAnalyzer
from modules.sentiment-analyzer import SentimentAnalyzer
from modules.ml-predictor import MLPredictor
from modules.visualization import ChartGenerator
from modules.pdf-generator import PDFReportGenerator

# Page config
st.set_page_config(
    page_title="Stock Analysis System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    h1 {color: #2c3e50; text-align: center; padding: 20px; background: white; 
        border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    div[data-testid="metric-container"] {background-color: white; border-radius: 10px; 
        padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .stButton>button {width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border-radius: 5px; padding: 10px; border: none; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Session state
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'ticker' not in st.session_state:
    st.session_state.ticker = None

# Title
st.title("📈 Advanced Stock Analysis & Prediction System")
st.markdown("**Professional AI-powered stock analysis**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔍 Stock Search")
    
    search_method = st.radio("Search by:", ["Company Name", "Ticker Symbol"])
    
    if search_method == "Company Name":
        st.info("💡 Enter: 'Reliance', 'TCS', 'Bank of Baroda'")
        company_name = st.text_input("Company Name:", placeholder="e.g., Bank of Baroda")
        
        if st.button("🔎 Find Ticker"):
            if company_name:
                with st.spinner("Searching..."):
                    fetcher = StockDataFetcher()
                    result = fetcher.lookup_ticker(company_name)
                    
                    if result:
                        st.success(f"✅ Found: {result['name']}")
                        st.session_state.ticker = result['symbol']
                        st.write(f"**Ticker:** {result['symbol']}")
                    else:
                        st.error("❌ Not found. Try manual entry.")
            else:
                st.warning("⚠️ Please enter company name")
    
    else:
        st.info("💡 For Indian stocks: add .NS or .BO")
        st.info("Examples: RELIANCE.NS, TCS.NS, SBIN.NS")
        ticker = st.text_input("Ticker Symbol:", placeholder="e.g., RELIANCE.NS")
        if ticker:
            st.session_state.ticker = ticker
    
    st.markdown("---")
    st.header("⚙️ Settings")
    
    time_period = st.selectbox("Time Period:", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
    st.markdown("### Technical Indicators")
    show_sma = st.checkbox("SMA", value=True)
    show_rsi = st.checkbox("RSI", value=True)
    show_macd = st.checkbox("MACD", value=True)
    
    st.markdown("---")
    st.header("🎯 Actions")
    
    if st.button("🔎 ANALYZE STOCK", type="primary"):
        if st.session_state.ticker:
            with st.spinner("🔄 Analyzing..."):
                try:
                    # Fetch data
                    st.info("📊 Fetching data...")
                    fetcher = StockDataFetcher()
                    data = fetcher.get_historical_data(st.session_state.ticker, period=time_period)
                    
                    if data is None or data.empty:
                        st.error("❌ Could not fetch data")
                        st.stop()
                    
                    fundamentals = fetcher.get_fundamentals(st.session_state.ticker)
                    
                    # Technical analysis
                    st.info("📈 Calculating indicators...")
                    analyzer = TechnicalAnalyzer()
                    data = analyzer.add_all_indicators(data)
                    signals = analyzer.generate_signals(data)
                    
                    # Sentiment
                    st.info("📰 Analyzing news...")
                    sentiment_analyzer = SentimentAnalyzer()
                    company = st.session_state.ticker.split('.')[0]
                    news = sentiment_analyzer.get_stock_news(company)
                    sentiment = sentiment_analyzer.analyze_sentiment(news)
                    
                    # Prediction
                    st.info("🤖 Making prediction...")
                    predictor = MLPredictor()
                    prediction, confidence = predictor.predict(data, fundamentals, sentiment, st.session_state.ticker)
                    
                    # Store results
                    st.session_state.analysis_data = {
                        'data': data, 'fundamentals': fundamentals,
                        'news': news, 'sentiment': sentiment,
                        'prediction': prediction, 'confidence': confidence,
                        'signals': signals
                    }
                    
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Enter ticker first")
    
    if st.button("📄 Generate Report"):
        if st.session_state.analysis_data:
            with st.spinner("📄 Generating..."):
                try:
                    generator = PDFReportGenerator()
                    pdf_bytes = generator.generate_report(st.session_state.ticker, st.session_state.analysis_data)
                    
                    st.download_button(
                        "📥 Download Report",
                        data=pdf_bytes,
                        file_name=f"{st.session_state.ticker}_report.txt",
                        mime="text/plain"
                    )
                    st.success("✅ Report ready!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Run analysis first")

# Main content
if st.session_state.analysis_data:
    d = st.session_state.analysis_data
    df = d['data']
    current = df['Close'].iloc[-1]
    pred = d['prediction']
    change = ((pred - current) / current) * 100
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"₹{current:.2f}")
    with col2:
        st.metric("Predicted Price", f"₹{pred:.2f}", f"{change:+.2f}%")
    with col3:
        signal = "BUY 📈" if change > 2 else "SELL 📉" if change < -2 else "HOLD ↔️"
        st.metric("Signal", signal)
    with col4:
        st.metric("Confidence", f"{d['confidence']:.1%}")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Technical", "💼 Fundamentals", "📰 News", "🤖 AI"])
    
    with tab1:
        st.subheader("📊 Price Chart")
        chart_gen = ChartGenerator()
        fig = chart_gen.create_candlestick(df, pred)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🎯 Signals")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Overall:** {d['signals'].get('Overall', 'N/A')}")
            st.info(f"**Recommendation:** {d['signals'].get('Recommendation', 'N/A')}")
        with col2:
            st.info(f"**RSI:** {d['signals'].get('RSI', 'N/A')}")
            st.info(f"**MACD:** {d['signals'].get('MACD', 'N/A')}")
    
    with tab2:
        st.subheader("📈 Technical Indicators")
        col1, col2 = st.columns(2)
        
        with col1:
            if show_rsi and 'RSI' in df.columns:
                fig_rsi = chart_gen.create_rsi_chart(df)
                st.plotly_chart(fig_rsi, use_container_width=True)
        
        with col2:
            if show_macd and 'MACD' in df.columns:
                fig_macd = chart_gen.create_macd_chart(df)
                st.plotly_chart(fig_macd, use_container_width=True)
    
    with tab3:
        st.subheader("💼 Fundamentals")
        if d['fundamentals']:
            fund_df = pd.DataFrame(d['fundamentals'].items(), columns=['Metric', 'Value'])
            st.dataframe(fund_df, use_container_width=True, hide_index=True)
        else:
            st.info("Data not available")
    
    with tab4:
        st.subheader("📰 News & Sentiment")
        st.metric("Sentiment Score", f"{d['sentiment']:.2f}")
        
        if d['sentiment'] > 0.6:
            st.success("Positive 😊")
        elif d['sentiment'] < 0.4:
            st.error("Negative 😟")
        else:
            st.warning("Neutral 😐")
        
        st.markdown("---")
        
        if d['news']:
            for i, article in enumerate(d['news'][:10], 1):
                with st.expander(f"{i}. {article.get('title', 'No title')}"):
                    st.write(f"**Source:** {article.get('source', 'Unknown')}")
                    st.write(f"**Sentiment:** {article.get('sentiment', 'Neutral')}")
        else:
            st.info("No news available")
    
    with tab5:
        st.subheader("🤖 AI Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Prediction")
            st.write(f"**Current:** ₹{current:.2f}")
            st.write(f"**Predicted:** ₹{pred:.2f}")
            st.write(f"**Change:** {change:+.2f}%")
            st.write(f"**Confidence:** {d['confidence']:.1%}")
        
        with col2:
            st.markdown("### Risk")
            vol = df['Close'].tail(20).std() / df['Close'].tail(20).mean() * 100
            if vol > 5:
                st.error(f"**High Risk** ⚠️\nVolatility: {vol:.2f}%")
            elif vol > 2:
                st.warning(f"**Medium Risk** ⚡\nVolatility: {vol:.2f}%")
            else:
                st.success(f"**Low Risk** ✅\nVolatility: {vol:.2f}%")

else:
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h2>👋 Welcome!</h2>
        <p style='font-size: 18px;'>Search for a stock in the sidebar to begin</p>
        <br>
        <p><b>Features:</b></p>
        <ul style='list-style: none;'>
            <li>📊 Technical Analysis</li>
            <li>💼 Fundamental Metrics</li>
            <li>📰 News Sentiment</li>
            <li>🤖 AI Predictions</li>
            <li>📄 PDF Reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Popular Stocks")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Large Cap:**\nRELIANCE.NS\nTCS.NS\nHDFCBANK.NS")
    with col2:
        st.info("**Banking:**\nSBIN.NS\nICICIBANK.NS\nBANKBARODA.NS")
    with col3:
        st.info("**IT Sector:**\nWIPRO.NS\nTECHM.NS\nHCLTECH.NS")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>Made with ❤️ using Streamlit | Stock Analysis System v2.0</p>
    <p>Data: Yahoo Finance | For educational purposes only</p>
</div>
""", unsafe_allow_html=True)