# ============================================================================
# FILE 4: modules/technical_analysis.py
# ============================================================================
# PURPOSE: Calculate technical indicators for stock analysis
#          - Moving Averages (SMA, EMA)
#          - RSI (Relative Strength Index)
#          - MACD (Moving Average Convergence Divergence)
#          - Bollinger Bands
#          - And more!
# ============================================================================

import pandas as pd
import numpy as np
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator


class TechnicalAnalyzer:
    """
    A class to calculate technical indicators.
    
    What it does:
    1. Adds moving averages (SMA, EMA)
    2. Calculates momentum indicators (RSI, Stochastic)
    3. Computes trend indicators (MACD, ADX)
    4. Calculates volatility (Bollinger Bands, ATR)
    5. Generates trading signals
    """
    
    def __init__(self):
        """Initialize the technical analyzer"""
        print("✅ TechnicalAnalyzer initialized")
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add ALL technical indicators to the dataframe.
        
        EXAMPLE:
        Input: DataFrame with columns [Open, High, Low, Close, Volume]
        Output: Same DataFrame + 15 new indicator columns
        
        Args:
            df: DataFrame with price data
        
        Returns:
            DataFrame with all indicators added
        """
        try:
            print("📈 Calculating technical indicators...")
            
            # Make a copy to avoid modifying original data
            data = df.copy()
            
            # ============================================================
            # 1. MOVING AVERAGES (Trend Following)
            # ============================================================
            # Simple Moving Average - average price over N days
            data['SMA_20'] = SMAIndicator(data['Close'], window=20).sma_indicator()
            data['SMA_50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
            data['SMA_200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
            
            # Exponential Moving Average - gives more weight to recent prices
            data['EMA_20'] = EMAIndicator(data['Close'], window=20).ema_indicator()
            data['EMA_50'] = EMAIndicator(data['Close'], window=50).ema_indicator()
            
            print("  ✓ Moving averages calculated")
            
            # ============================================================
            # 2. RSI - Relative Strength Index (Momentum)
            # ============================================================
            # RSI shows if stock is overbought (>70) or oversold (<30)
            # Range: 0 to 100
            data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
            
            print("  ✓ RSI calculated")
            
            # ============================================================
            # 3. MACD - Moving Average Convergence Divergence (Trend)
            # ============================================================
            # MACD shows trend changes
            # When MACD > Signal = Bullish (buy signal)
            # When MACD < Signal = Bearish (sell signal)
            macd = MACD(data['Close'])
            data['MACD'] = macd.macd()                    # MACD line
            data['MACD_Signal'] = macd.macd_signal()      # Signal line
            data['MACD_Hist'] = macd.macd_diff()          # Histogram (difference)
            
            print("  ✓ MACD calculated")
            
            # ============================================================
            # 4. BOLLINGER BANDS (Volatility)
            # ============================================================
            # Shows price volatility
            # Price near upper band = might go down
            # Price near lower band = might go up
            bb = BollingerBands(data['Close'])
            data['BB_Upper'] = bb.bollinger_hband()       # Upper band
            data['BB_Lower'] = bb.bollinger_lband()       # Lower band
            data['BB_Middle'] = bb.bollinger_mavg()       # Middle band (SMA)
            
            print("  ✓ Bollinger Bands calculated")
            
            # ============================================================
            # 5. ATR - Average True Range (Volatility)
            # ============================================================
            # Measures volatility - higher ATR = more volatile
            atr = AverageTrueRange(data['High'], data['Low'], data['Close'])
            data['ATR'] = atr.average_true_range()
            
            print("  ✓ ATR calculated")
            
            # ============================================================
            # 6. STOCHASTIC OSCILLATOR (Momentum)
            # ============================================================
            # Shows momentum - similar to RSI
            # Range: 0 to 100
            stoch = StochasticOscillator(data['High'], data['Low'], data['Close'])
            data['Stoch_K'] = stoch.stoch()               # %K line
            data['Stoch_D'] = stoch.stoch_signal()        # %D line (signal)
            
            print("  ✓ Stochastic calculated")
            
            # ============================================================
            # 7. ADX - Average Directional Index (Trend Strength)
            # ============================================================
            # Shows trend strength (not direction!)
            # ADX > 25 = Strong trend
            # ADX < 20 = Weak/No trend
            adx = ADXIndicator(data['High'], data['Low'], data['Close'])
            data['ADX'] = adx.adx()
            
            print("  ✓ ADX calculated")
            
            # ============================================================
            # 8. OBV - On Balance Volume (Volume)
            # ============================================================
            # Shows volume flow - helps confirm trends
            obv = OnBalanceVolumeIndicator(data['Close'], data['Volume'])
            data['OBV'] = obv.on_balance_volume()
            
            print("  ✓ OBV calculated")
            
            # ============================================================
            # 9. MFI - Money Flow Index (Volume + Price)
            # ============================================================
            # Like RSI but includes volume
            # Range: 0 to 100
            mfi = MFIIndicator(data['High'], data['Low'], data['Close'], data['Volume'])
            data['MFI'] = mfi.money_flow_index()
            
            print("  ✓ MFI calculated")
            
            # ============================================================
            # 10. VOLUME INDICATORS
            # ============================================================
            # Simple moving average of volume
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            
            print("  ✓ Volume indicators calculated")
            
            print("✅ All technical indicators calculated successfully!")
            return data
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            # If error, return original data without indicators
            return df
    
    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        Generate trading signals based on indicators.
        
        EXAMPLE:
        Input: DataFrame with indicators
        Output: {'RSI': 'OVERSOLD', 'MACD': 'BULLISH', 'Trend': 'UPTREND'}
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            Dictionary with signals
        """
        signals = {}
        
        try:
            print("🎯 Generating trading signals...")
            
            # Get the most recent values (last row)
            latest = df.iloc[-1]
            
            # ============================================================
            # RSI SIGNAL
            # ============================================================
            rsi = latest['RSI']
            if rsi > 70:
                signals['RSI'] = 'OVERBOUGHT'  # Stock might be too expensive
                signals['RSI_Action'] = 'Consider SELLING'
            elif rsi < 30:
                signals['RSI'] = 'OVERSOLD'    # Stock might be too cheap
                signals['RSI_Action'] = 'Consider BUYING'
            else:
                signals['RSI'] = 'NEUTRAL'     # Normal range
                signals['RSI_Action'] = 'HOLD'
            
            # ============================================================
            # MACD SIGNAL
            # ============================================================
            macd = latest['MACD']
            signal = latest['MACD_Signal']
            
            if macd > signal:
                signals['MACD'] = 'BULLISH'    # Upward momentum
                signals['MACD_Action'] = 'Buy signal'
            else:
                signals['MACD'] = 'BEARISH'    # Downward momentum
                signals['MACD_Action'] = 'Sell signal'
            
            # ============================================================
            # MOVING AVERAGE TREND
            # ============================================================
            close = latest['Close']
            sma_50 = latest['SMA_50']
            sma_200 = latest['SMA_200']
            
            if pd.notna(sma_50) and pd.notna(sma_200):
                if close > sma_50 > sma_200:
                    signals['Trend'] = 'STRONG UPTREND'
                    signals['Trend_Action'] = 'Bullish - Consider buying'
                elif close < sma_50 < sma_200:
                    signals['Trend'] = 'STRONG DOWNTREND'
                    signals['Trend_Action'] = 'Bearish - Consider selling'
                elif close > sma_50:
                    signals['Trend'] = 'UPTREND'
                    signals['Trend_Action'] = 'Positive'
                elif close < sma_50:
                    signals['Trend'] = 'DOWNTREND'
                    signals['Trend_Action'] = 'Negative'
                else:
                    signals['Trend'] = 'SIDEWAYS'
                    signals['Trend_Action'] = 'Neutral'
            
            # ============================================================
            # BOLLINGER BANDS SIGNAL
            # ============================================================
            bb_upper = latest['BB_Upper']
            bb_lower = latest['BB_Lower']
            
            if close >= bb_upper:
                signals['Bollinger'] = 'AT UPPER BAND'
                signals['Bollinger_Action'] = 'Might reverse down'
            elif close <= bb_lower:
                signals['Bollinger'] = 'AT LOWER BAND'
                signals['Bollinger_Action'] = 'Might reverse up'
            else:
                signals['Bollinger'] = 'MIDDLE RANGE'
                signals['Bollinger_Action'] = 'Normal'
            
            # ============================================================
            # STOCHASTIC SIGNAL
            # ============================================================
            stoch_k = latest['Stoch_K']
            
            if stoch_k > 80:
                signals['Stochastic'] = 'OVERBOUGHT'
            elif stoch_k < 20:
                signals['Stochastic'] = 'OVERSOLD'
            else:
                signals['Stochastic'] = 'NEUTRAL'
            
            # ============================================================
            # OVERALL RECOMMENDATION
            # ============================================================
            # Count bullish vs bearish signals
            bullish_count = 0
            bearish_count = 0
            
            if signals['RSI'] == 'OVERSOLD':
                bullish_count += 1
            elif signals['RSI'] == 'OVERBOUGHT':
                bearish_count += 1
            
            if signals['MACD'] == 'BULLISH':
                bullish_count += 1
            elif signals['MACD'] == 'BEARISH':
                bearish_count += 1
            
            if 'UPTREND' in signals.get('Trend', ''):
                bullish_count += 1
            elif 'DOWNTREND' in signals.get('Trend', ''):
                bearish_count += 1
            
            # Make overall recommendation
            if bullish_count > bearish_count:
                signals['Overall'] = 'BULLISH 📈'
                signals['Recommendation'] = 'BUY'
            elif bearish_count > bullish_count:
                signals['Overall'] = 'BEARISH 📉'
                signals['Recommendation'] = 'SELL'
            else:
                signals['Overall'] = 'NEUTRAL ↔️'
                signals['Recommendation'] = 'HOLD'
            
            print(f"✅ Signals generated: {signals['Overall']}")
            return signals
            
        except Exception as e:
            print(f"❌ Error generating signals: {e}")
            return {'Error': 'Could not generate signals'}
    
    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> dict:
        """
        Calculate support and resistance levels.
        
        Support = Price level where stock tends to stop falling
        Resistance = Price level where stock tends to stop rising
        
        Args:
            df: DataFrame with price data
            window: Number of days to look back
        
        Returns:
            Dictionary with support and resistance levels
        """
        try:
            # Get recent data
            recent = df.tail(window)
            
            # Support = Recent low prices
            support = recent['Low'].min()
            
            # Resistance = Recent high prices
            resistance = recent['High'].max()
            
            # Current price
            current = df['Close'].iloc[-1]
            
            return {
                'support': support,
                'resistance': resistance,
                'current': current,
                'distance_to_support': ((current - support) / support) * 100,
                'distance_to_resistance': ((resistance - current) / current) * 100
            }
        except:
            return {}


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.technical_analysis import TechnicalAnalyzer
# 
# # Create analyzer object
# analyzer = TechnicalAnalyzer()
# 
# # Add indicators to your data
# df_with_indicators = analyzer.add_all_indicators(price_data)
# 
# # Generate signals
# signals = analyzer.generate_signals(df_with_indicators)
# print(signals['Overall'])  # Output: "BULLISH 📈"
# print(signals['Recommendation'])  # Output: "BUY"
# 
# # Get support/resistance
# levels = analyzer.get_support_resistance(df_with_indicators)
# print(f"Support: {levels['support']}")
# print(f"Resistance: {levels['resistance']}")
# 
# ============================================================================