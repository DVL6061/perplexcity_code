# ============================================================================
# FILE 2: modules/__init__.py
# ============================================================================
# PURPOSE: This file tells Python that 'modules' is a package
#          It allows importing modules from this folder
# HOW TO USE: Just create this file - no need to edit it
# ============================================================================

"""
Advanced Stock Analysis System - Core Modules
==============================================

This package contains all the core modules for stock analysis:
- data_fetcher: Gets stock data from Yahoo Finance
- technical_analysis: Calculates technical indicators
- sentiment_analyzer: Analyzes news sentiment
- ml_predictor: Machine learning predictions
- visualization: Creates interactive charts
- pdf_generator: Generates PDF reports
"""

# Version information
__version__ = "2.0.0"
__author__ = "Stock Analysis Team"

# You can import all modules from this package
__all__ = [
    'data_fetcher',
    'technical_analysis', 
    'sentiment_analyzer',
    'ml_predictor',
    'visualization',
    'pdf_generator'
]