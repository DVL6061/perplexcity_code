# ============================================================================
# FILE 8: modules/pdf_generator.py (SIMPLIFIED VERSION)
# ============================================================================
# PURPOSE: Generate PDF reports (simplified without WeasyPrint)
#          This version creates a simple text report
#          You can upgrade to fancy PDF with WeasyPrint later
# ============================================================================

from datetime import datetime
import io


class PDFReportGenerator:
    """
    A class to generate PDF reports (simplified version).
    
    NOTE: This is a simplified version that creates text-based reports.
    For production, you can add WeasyPrint to create fancy PDF with charts.
    """
    
    def __init__(self):
        """Initialize the PDF generator"""
        print("✅ PDFReportGenerator initialized")
    
    def generate_report(self, ticker: str, analysis_data: dict) -> bytes:
        """
        Generate a PDF report (simplified text version).
        
        Args:
            ticker: Stock ticker symbol
            analysis_data: Dictionary with all analysis results
        
        Returns:
            Bytes of the report (can be downloaded)
        """
        try:
            print(f"📄 Generating report for {ticker}...")
            
            # Extract data
            data = analysis_data.get('data')
            fundamentals = analysis_data.get('fundamentals', {})
            news = analysis_data.get('news', [])
            sentiment = analysis_data.get('sentiment', 0.5)
            prediction = analysis_data.get('prediction', 0)
            confidence = analysis_data.get('confidence', 0)
            
            current_price = data['Close'].iloc[-1] if data is not None else 0
            
            # Create report content
            report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    STOCK ANALYSIS REPORT                                ║
║                    {ticker}                                              ║
║                    {datetime.now().strftime('%B %d, %Y')}               ║
╚══════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Price:      ₹{current_price:.2f}
Predicted Price:    ₹{prediction:.2f}
Expected Change:    {((prediction - current_price) / current_price * 100):+.2f}%
Model Confidence:   {confidence:.1%}

Recommendation:     {'BUY 📈' if prediction > current_price * 1.02 else 'SELL 📉' if prediction < current_price * 0.98 else 'HOLD ↔️'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 FUNDAMENTAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            # Add fundamentals
            if fundamentals:
                for key, value in fundamentals.items():
                    report += f"{key:.<30} {value}\n"
            else:
                report += "Fundamental data not available\n"
            
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📰 NEWS SENTIMENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Sentiment Score: {sentiment:.2f}/1.00
Interpretation: {'Very Positive 😊' if sentiment > 0.7 else 'Positive 🙂' if sentiment > 0.6 else 'Neutral 😐' if sentiment > 0.4 else 'Negative 😟' if sentiment > 0.3 else 'Very Negative 😢'}

Recent News Headlines:
"""
            
            # Add news
            if news:
                for i, article in enumerate(news[:5], 1):
                    report += f"\n{i}. {article.get('title', 'No title')}\n"
                    report += f"   Source: {article.get('source', 'Unknown')} | "
                    report += f"Date: {article.get('date', 'Unknown')}\n"
                    report += f"   Sentiment: {article.get('sentiment', 'Neutral')}\n"
            else:
                report += "\nNo recent news available\n"
            
            # Technical signals
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 TECHNICAL INDICATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                
                if 'RSI' in latest:
                    rsi = latest['RSI']
                    report += f"RSI (14):               {rsi:.2f} "
                    report += f"({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})\n"
                
                if 'MACD' in latest:
                    macd = latest['MACD']
                    signal = latest['MACD_Signal']
                    report += f"MACD:                   {macd:.2f}\n"
                    report += f"Signal Line:            {signal:.2f} "
                    report += f"({'Bullish' if macd > signal else 'Bearish'})\n"
                
                if 'SMA_50' in latest:
                    sma_50 = latest['SMA_50']
                    report += f"SMA (50):               ₹{sma_50:.2f}\n"
                
                if 'SMA_200' in latest:
                    sma_200 = latest['SMA_200']
                    report += f"SMA (200):              ₹{sma_200:.2f}\n"
            
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI PREDICTION INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model Type:             XGBoost Regressor
Prediction Horizon:     Next Trading Day
Confidence Level:       {confidence:.1%}

Risk Assessment:        {self._get_risk_level(prediction, current_price)}

Trading Recommendations:
• {self._get_recommendations(prediction, current_price, sentiment)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This report is for informational purposes only and should not be considered
as financial advice. Stock market investments are subject to market risks.
Please consult a certified financial advisor before making investment decisions.

Past performance is not indicative of future results.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by: Advanced Stock Analysis System
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # Convert to bytes
            report_bytes = report.encode('utf-8')
            
            print("✅ Report generated successfully")
            return report_bytes
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            error_report = f"Error generating report: {str(e)}"
            return error_report.encode('utf-8')
    
    def _get_risk_level(self, prediction: float, current: float) -> str:
        """Get risk level based on prediction."""
        change_pct = abs((prediction - current) / current * 100)
        
        if change_pct > 5:
            return "HIGH ⚠️"
        elif change_pct > 2:
            return "MEDIUM ⚡"
        else:
            return "LOW ✅"
    
    def _get_recommendations(self, prediction: float, current: float, sentiment: float) -> str:
        """Get trading recommendations."""
        change_pct = (prediction - current) / current * 100
        
        recommendations = []
        
        if change_pct > 2:
            recommendations.append("Consider BUYING on dips")
            recommendations.append("Set stop loss at 3-5% below entry")
        elif change_pct < -2:
            recommendations.append("Consider SELLING or taking profits")
            recommendations.append("Avoid fresh buying")
        else:
            recommendations.append("HOLD current positions")
            recommendations.append("Wait for clearer signals")
        
        if sentiment > 0.6:
            recommendations.append("Positive news sentiment supports upside")
        elif sentiment < 0.4:
            recommendations.append("Negative sentiment may pressure prices")
        
        return "\n• ".join(recommendations)


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.pdf_generator import PDFReportGenerator
# import streamlit as st
# 
# # Create generator
# generator = PDFReportGenerator()
# 
# # Generate report
# pdf_bytes = generator.generate_report(ticker, analysis_data)
# 
# # Offer download in Streamlit
# st.download_button(
#     label="📄 Download Report",
#     data=pdf_bytes,
#     file_name=f"{ticker}_report.txt",
#     mime="text/plain"
# )
# 
# ============================================================================