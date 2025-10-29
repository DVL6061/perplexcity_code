# ============================================================================
# FILE 6: modules/ml_predictor.py (SIMPLIFIED BUT WORKING VERSION)
# ============================================================================
# PURPOSE: Machine Learning predictions for stock prices
#          - Train XGBoost model
#          - Make predictions
#          - Save/load models
# ============================================================================

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import os
from datetime import datetime


class MLPredictor:
    """
    A class for machine learning price predictions.
    
    What it does:
    1. Prepares features from price data and indicators
    2. Trains XGBoost model
    3. Makes next-day price predictions
    4. Saves/loads models
    """
    
    def __init__(self):
        """Initialize the ML predictor"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        print("✅ MLPredictor initialized")
    
    def prepare_features(self, df: pd.DataFrame, fundamentals: dict, 
                        sentiment_score: float) -> pd.DataFrame:
        """
        Prepare features for ML model.
        
        Args:
            df: DataFrame with price data and indicators
            fundamentals: Dictionary with fundamental metrics
            sentiment_score: News sentiment score (0 to 1)
        
        Returns:
            DataFrame with features ready for ML
        """
        try:
            print("🔧 Preparing ML features...")
            
            # Make a copy
            data = df.copy()
            
            # ============================================================
            # PRICE-BASED FEATURES
            # ============================================================
            # Daily returns (percentage change)
            data['Returns'] = data['Close'].pct_change()
            
            # Price lags (previous days' prices)
            data['Close_Lag1'] = data['Close'].shift(1)   # Yesterday's price
            data['Close_Lag5'] = data['Close'].shift(5)   # 5 days ago
            data['Close_Lag10'] = data['Close'].shift(10) # 10 days ago
            
            # Rolling statistics
            data['Close_Rolling_Mean_5'] = data['Close'].rolling(window=5).mean()
            data['Close_Rolling_Std_5'] = data['Close'].rolling(window=5).std()
            data['Volume_Rolling_Mean_5'] = data['Volume'].rolling(window=5).mean()
            
            # ============================================================
            # FUNDAMENTAL FEATURES (from company data)
            # ============================================================
            # Add fundamentals as constant values
            if fundamentals:
                pe_ratio = fundamentals.get('P/E Ratio', 0)
                if pe_ratio != 'N/A' and pe_ratio is not None:
                    data['PE_Ratio'] = float(pe_ratio)
                else:
                    data['PE_Ratio'] = 0
            else:
                data['PE_Ratio'] = 0
            
            # ============================================================
            # SENTIMENT FEATURE
            # ============================================================
            # Add sentiment score
            data['Sentiment'] = sentiment_score
            
            # ============================================================
            # TARGET VARIABLE (what we want to predict)
            # ============================================================
            # Next day's closing price
            data['Target'] = data['Close'].shift(-1)  # Shift backward = future price
            
            # Drop rows with NaN values
            data = data.dropna()
            
            print(f"✅ Prepared {len(data)} rows with features")
            return data
            
        except Exception as e:
            print(f"❌ Error preparing features: {e}")
            return df
    
    def train(self, ticker: str, df: pd.DataFrame, fundamentals: dict, 
             sentiment_score: float) -> bool:
        """
        Train the ML model.
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with price data and indicators
            fundamentals: Company fundamentals
            sentiment_score: News sentiment
        
        Returns:
            True if training successful, False otherwise
        """
        try:
            print(f"🎓 Training model for {ticker}...")
            
            # Prepare features
            data = self.prepare_features(df, fundamentals, sentiment_score)
            
            if len(data) < 100:  # Need at least 100 days of data
                print("❌ Not enough data to train (need at least 100 days)")
                return False
            
            # ============================================================
            # SELECT FEATURES FOR TRAINING
            # ============================================================
            feature_columns = [
                'Close', 'Volume', 'Returns',
                'Close_Lag1', 'Close_Lag5', 'Close_Lag10',
                'Close_Rolling_Mean_5', 'Close_Rolling_Std_5',
                'Volume_Rolling_Mean_5', 'PE_Ratio', 'Sentiment'
            ]
            
            # Add technical indicators if they exist
            indicator_columns = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI', 
                               'MACD', 'MACD_Signal', 'BB_Upper', 'BB_Lower']
            
            for col in indicator_columns:
                if col in data.columns:
                    feature_columns.append(col)
            
            # Keep only available features
            available_features = [col for col in feature_columns if col in data.columns]
            self.feature_names = available_features
            
            # Prepare X (features) and y (target)
            X = data[available_features].values
            y = data['Target'].values
            
            print(f"  Using {len(available_features)} features")
            
            # ============================================================
            # SPLIT DATA: 80% training, 20% testing
            # ============================================================
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False  # Don't shuffle time series!
            )
            
            # ============================================================
            # SCALE FEATURES (normalize to similar ranges)
            # ============================================================
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # ============================================================
            # TRAIN XGBOOST MODEL
            # ============================================================
            print("  🤖 Training XGBoost model...")
            
            self.model = xgb.XGBRegressor(
                n_estimators=100,      # Number of trees
                learning_rate=0.1,     # Learning rate
                max_depth=5,           # Tree depth
                random_state=42        # For reproducibility
            )
            
            # Train the model
            self.model.fit(X_train_scaled, y_train)
            
            # ============================================================
            # EVALUATE MODEL
            # ============================================================
            # Make predictions on test set
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate accuracy (R-squared score)
            from sklearn.metrics import r2_score, mean_absolute_error
            
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            print(f"  ✅ Model trained successfully!")
            print(f"  📊 R² Score: {r2:.4f}")
            print(f"  📊 MAE: ₹{mae:.2f}")
            
            # ============================================================
            # SAVE MODEL
            # ============================================================
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            
            # Save model and scaler
            model_path = f'models/{ticker}_model.joblib'
            scaler_path = f'models/{ticker}_scaler.joblib'
            features_path = f'models/{ticker}_features.joblib'
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.feature_names, features_path)
            
            print(f"  💾 Model saved to {model_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return False
    
    def load_model(self, ticker: str) -> bool:
        """
        Load a previously trained model.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            True if model loaded, False otherwise
        """
        try:
            model_path = f'models/{ticker}_model.joblib'
            scaler_path = f'models/{ticker}_scaler.joblib'
            features_path = f'models/{ticker}_features.joblib'
            
            # Check if files exist
            if not os.path.exists(model_path):
                return False
            
            # Load model, scaler, and features
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(features_path)
            
            print(f"✅ Model loaded from {model_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict(self, df: pd.DataFrame, fundamentals: dict, 
               sentiment_score: float, ticker: str = None) -> tuple:
        """
        Make price prediction.
        
        Args:
            df: DataFrame with price data and indicators
            fundamentals: Company fundamentals
            sentiment_score: News sentiment
            ticker: Stock ticker (to load saved model)
        
        Returns:
            Tuple of (predicted_price, confidence)
        """
        try:
            print("🔮 Making prediction...")
            
            # Try to load existing model
            if ticker and not self.model:
                self.load_model(ticker)
            
            # If no model, train a new one
            if not self.model:
                print("  No model found, training new model...")
                if ticker:
                    success = self.train(ticker, df, fundamentals, sentiment_score)
                    if not success:
                        return self._simple_prediction(df)
                else:
                    return self._simple_prediction(df)
            
            # Prepare features
            data = self.prepare_features(df, fundamentals, sentiment_score)
            
            # Get latest data point
            latest = data.iloc[[-1]][self.feature_names]
            
            # Scale features
            latest_scaled = self.scaler.transform(latest)
            
            # Make prediction
            predicted_price = self.model.predict(latest_scaled)[0]
            
            # Calculate confidence (simplified - based on recent volatility)
            recent_std = df['Close'].tail(20).std()
            recent_mean = df['Close'].tail(20).mean()
            volatility = recent_std / recent_mean
            
            # Confidence: lower volatility = higher confidence
            confidence = max(0.5, min(0.95, 1 - volatility))
            
            print(f"✅ Predicted price: ₹{predicted_price:.2f}")
            print(f"  Confidence: {confidence:.2%}")
            
            return predicted_price, confidence
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._simple_prediction(df)
    
    def _simple_prediction(self, df: pd.DataFrame) -> tuple:
        """
        Simple fallback prediction using moving average.
        
        Args:
            df: DataFrame with price data
        
        Returns:
            Tuple of (predicted_price, confidence)
        """
        print("  ⚠️ Using simple prediction (moving average)")
        
        # Use 5-day moving average as prediction
        recent = df['Close'].tail(5)
        prediction = recent.mean()
        
        # Low confidence for simple prediction
        confidence = 0.5
        
        return prediction, confidence


# ============================================================================
# HOW TO USE THIS MODULE:
# ============================================================================
# 
# from modules.ml_predictor import MLPredictor
# 
# # Create predictor
# predictor = MLPredictor()
# 
# # Make prediction
# predicted_price, confidence = predictor.predict(
#     df=price_data,
#     fundamentals=fundamental_data,
#     sentiment_score=0.7,
#     ticker='RELIANCE.NS'
# )
# 
# print(f"Predicted next close: ₹{predicted_price:.2f}")
# print(f"Confidence: {confidence:.1%}")
# 
# ============================================================================