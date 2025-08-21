# Stock Analysis Dashboard

## Overview

A Streamlit-based web application for financial market analysis and stock data visualization. The application provides an interactive dashboard for analyzing stock performance with real-time data from Yahoo Finance, featuring customizable charts, technical indicators, and comprehensive market metrics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for rapid web app development
- **UI Design**: Custom CSS styling with dark theme optimizations
- **Layout**: Wide layout with expandable sidebar for controls
- **Responsive Design**: Configurable page layout with custom styling classes

### Data Visualization
- **Charting Library**: Plotly for interactive financial charts
- **Chart Types**: Multiple chart types including candlestick, line charts, and subplots
- **Interactive Features**: Real-time data updates and user-controlled visualizations

### Data Processing
- **Financial Data**: Yahoo Finance API integration via yfinance library
- **Data Manipulation**: Pandas for data processing and analysis
- **Mathematical Operations**: NumPy for numerical computations
- **Date Handling**: Built-in datetime libraries for time series operations

### Application Structure
- **Single-file Architecture**: Monolithic structure in app.py
- **Component-based UI**: Modular Streamlit components with custom styling
- **State Management**: Streamlit's built-in session state management

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance data retrieval
- **plotly**: Interactive charting and visualization
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

### Data Sources
- **Yahoo Finance API**: Real-time and historical stock market data
- **Financial Markets**: Stock prices, trading volumes, and market indicators

### Styling and UI
- **Custom CSS**: Enhanced dark theme with branded color scheme (#00ff88 accent)
- **Plotly Themes**: Interactive chart styling and customization
- **Streamlit Components**: Native UI elements with custom overrides