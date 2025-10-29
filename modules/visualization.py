# ============================================================================
# FILE 7: modules/visualization.py
# ============================================================================
# PURPOSE: Create interactive charts using Plotly
#          - Candlestick charts
#          - Technical indicator charts
#          - Prediction visualization
# ============================================================================

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class ChartGenerator:
    """
    A class to create interactive charts.
    
    What it does:
    1. Creates candlestick charts with volume
    2. Plots technical indicators
    3. Shows predictions
    4. Makes interactive charts you can zoom/pan
    """
    
    def __init__(self):
        """Initialize the chart generator"""
        print("✅ ChartGenerator initialized")
    
    def create_candlestick(self, df: pd.DataFrame, prediction: float = None) -> go.Figure:
        """
        Create interactive candlestick chart with volume.
        
        Args:
            df: DataFrame with OHLCV data and indicators
            prediction: Predicted next price (optional)
        
        Returns:
            Plotly figure object
        """
        try:
            print("📊 Creating candlestick chart...")
            
            # Create figure with 2 rows: price chart + volume chart
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.7, 0.3],  # Price chart bigger than volume
                subplot_titles=('Price Chart', 'Volume')
            )
            
            # ============================================================
            # 1. CANDLESTICK CHART
            # ============================================================
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price',
                    increasing_line_color='green',  # Green for up days
                    decreasing_line_color='red'     # Red for down days
                ),
                row=1, col=1
            )
            
            # ============================================================
            # 2. ADD MOVING AVERAGES (if available)
            # ============================================================
            if 'SMA_20' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'SMA_50' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            # ============================================================
            # 3. ADD PREDICTION (if provided)
            # ============================================================
            if prediction:
                # Get last date
                last_date = df.index[-1]
                
                # Add prediction point
                fig.add_trace(
                    go.Scatter(
                        x=[last_date],
                        y=[prediction],
                        mode='markers',
                        name='Predicted Price',
                        marker=dict(
                            size=15,
                            color='purple',
                            symbol='star',
                            line=dict(color='white', width=2)
                        )
                    ),
                    row=1, col=1
                )
            
            # ============================================================
            # 4. VOLUME CHART
            # ============================================================
            # Color volume bars: green if price up, red if price down
            colors = ['green' if close >= open else 'red' 
                     for close, open in zip(df['Close'], df['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # ============================================================
            # 5. UPDATE LAYOUT (make it look nice)
            # ============================================================
            fig.update_layout(
                title='Stock Price Analysis',
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                template='plotly_white',
                height=700,
                showlegend=True,
                hovermode='x unified'  # Show all values for a date
            )
            
            # Remove range slider (it's distracting)
            fig.update_xaxes(rangeslider_visible=False)
            
            print("✅ Candlestick chart created")
            return fig
            
        except Exception as e:
            print(f"❌ Error creating chart: {e}")
            return go.Figure()  # Return empty figure
    
    def create_rsi_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create RSI indicator chart.
        
        Args:
            df: DataFrame with RSI values
        
        Returns:
            Plotly figure
        """
        try:
            fig = go.Figure()
            
            # RSI line
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                )
            )
            
            # Add overbought line (70)
            fig.add_hline(
                y=70, 
                line_dash="dash", 
                line_color="red",
                annotation_text="Overbought (70)"
            )
            
            # Add oversold line (30)
            fig.add_hline(
                y=30, 
                line_dash="dash", 
                line_color="green",
                annotation_text="Oversold (30)"
            )
            
            # Layout
            fig.update_layout(
                title='RSI Indicator',
                xaxis_title='Date',
                yaxis_title='RSI',
                template='plotly_white',
                height=300,
                yaxis=dict(range=[0, 100])
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Error creating RSI chart: {e}")
            return go.Figure()
    
    def create_macd_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create MACD indicator chart.
        
        Args:
            df: DataFrame with MACD values
        
        Returns:
            Plotly figure
        """
        try:
            fig = go.Figure()
            
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue', width=2)
                )
            )
            
            # Signal line
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD_Signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='red', width=2)
                )
            )
            
            # Histogram
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['MACD_Hist'],
                    name='Histogram',
                    marker_color='gray'
                )
            )
            
            # Layout
            fig.update_layout(
                title='MACD Indicator',
                xaxis_title='Date',
                yaxis_title='MACD',
                template='plotly_white',
                height=300
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Error creating MACD chart: {e}")
            return go.Figure()


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.visualization import ChartGenerator
# import streamlit as st
# 
# # Create generator
# chart_gen = ChartGenerator()
# 
# # Create candlestick chart
# fig = chart_gen.create_candlestick(price_data, prediction=2500.50)
# 
# # Display in Streamlit
# st.plotly_chart(fig, use_container_width=True)
# 
# # Create RSI chart
# fig_rsi = chart_gen.create_rsi_chart(price_data)
# st.plotly_chart(fig_rsi)
# 
# ============================================================================