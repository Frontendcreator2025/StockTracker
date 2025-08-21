import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

# Configure page
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark theme styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #00ff88;
    }
    .metric-container {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00ff88;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #0e1117;
    }
    .stButton > button {
        background-color: #00ff88;
        color: #0e1117;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #00cc6a;
    }
</style>
""", unsafe_allow_html=True)

def get_stock_data(symbol, period="1y"):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            return None, None
        info = stock.info
        return data, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

def calculate_technical_indicators(data):
    """Calculate technical indicators"""
    if data is None or data.empty:
        return data
    
    # Moving averages
    data['MA_20'] = data['Close'].rolling(window=20).mean()
    data['MA_50'] = data['Close'].rolling(window=50).mean()
    
    # RSI calculation
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    data['BB_middle'] = data['Close'].rolling(window=20).mean()
    bb_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
    data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
    
    return data

def create_stock_chart(data, symbol, chart_type="candlestick"):
    """Create interactive stock chart with Plotly"""
    if data is None or data.empty:
        return None
    
    # Calculate technical indicators
    data = calculate_technical_indicators(data)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Stock Price', 'Volume', 'RSI'),
        row_width=[0.6, 0.2, 0.2]
    )
    
    # Main price chart
    if chart_type == "candlestick":
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Price",
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff6b6b'
            ),
            row=1, col=1
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name="Close Price",
                line=dict(color='#00ff88', width=2)
            ),
            row=1, col=1
        )
    
    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MA_20'],
            mode='lines',
            name="MA 20",
            line=dict(color='#ffa500', width=1)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MA_50'],
            mode='lines',
            name="MA 50",
            line=dict(color='#ff69b4', width=1)
        ),
        row=1, col=1
    )
    
    # Add Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['BB_upper'],
            mode='lines',
            name="BB Upper",
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['BB_lower'],
            mode='lines',
            name="BB Lower",
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(255,255,255,0.1)',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Volume chart
    colors = ['#00ff88' if close >= open else '#ff6b6b' 
              for close, open in zip(data['Close'], data['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name="Volume",
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # RSI chart
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['RSI'],
            mode='lines',
            name="RSI",
            line=dict(color='#00bfff', width=2),
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Add RSI reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Stock Analysis",
        xaxis_rangeslider_visible=False,
        height=800,
        template="plotly_dark",
        hovermode='x unified',
        font=dict(color='#fafafa'),
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117'
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Price ($)", row=1, col=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="Volume", row=2, col=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="RSI", row=3, col=1, gridcolor='rgba(255,255,255,0.1)', range=[0, 100])
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def format_large_number(num):
    """Format large numbers for display"""
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

def display_stock_info(info, current_price):
    """Display key stock information"""
    if not info:
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = format_large_number(market_cap)
        st.metric("Market Cap", market_cap)
        
        pe_ratio = info.get('trailingPE', 'N/A')
        if pe_ratio != 'N/A':
            pe_ratio = f"{pe_ratio:.2f}"
        st.metric("P/E Ratio", pe_ratio)
    
    with col2:
        dividend_yield = info.get('dividendYield', 'N/A')
        if dividend_yield != 'N/A':
            dividend_yield = f"{dividend_yield*100:.2f}%"
        st.metric("Dividend Yield", dividend_yield)
        
        beta = info.get('beta', 'N/A')
        if beta != 'N/A':
            beta = f"{beta:.2f}"
        st.metric("Beta", beta)
    
    with col3:
        volume = info.get('volume', 'N/A')
        if volume != 'N/A':
            volume = f"{volume:,}"
        st.metric("Volume", volume)
        
        avg_volume = info.get('averageVolume', 'N/A')
        if avg_volume != 'N/A':
            avg_volume = f"{avg_volume:,}"
        st.metric("Avg Volume", avg_volume)
    
    with col4:
        high_52w = info.get('fiftyTwoWeekHigh', 'N/A')
        if high_52w != 'N/A':
            high_52w = f"${high_52w:.2f}"
        st.metric("52W High", high_52w)
        
        low_52w = info.get('fiftyTwoWeekLow', 'N/A')
        if low_52w != 'N/A':
            low_52w = f"${low_52w:.2f}"
        st.metric("52W Low", low_52w)

def create_financial_summary_table(data, info, symbol):
    """Create a comprehensive financial summary table"""
    if data is None or data.empty:
        return None
    
    latest_data = data.iloc[-1]
    prev_data = data.iloc[-2] if len(data) > 1 else latest_data
    
    # Calculate changes
    price_change = latest_data['Close'] - prev_data['Close']
    price_change_pct = (price_change / prev_data['Close']) * 100
    
    # Create summary data
    summary_data = {
        'Metric': [
            'Current Price',
            'Previous Close',
            'Price Change',
            'Price Change %',
            'Open',
            'High',
            'Low',
            'Volume',
            'Market Cap',
            'P/E Ratio',
            'EPS',
            'Dividend Yield',
            'Beta',
            '52W High',
            '52W Low',
            'Average Volume'
        ],
        'Value': [
            f"${latest_data['Close']:.2f}",
            f"${prev_data['Close']:.2f}",
            f"${price_change:.2f}",
            f"{price_change_pct:.2f}%",
            f"${latest_data['Open']:.2f}",
            f"${latest_data['High']:.2f}",
            f"${latest_data['Low']:.2f}",
            f"{latest_data['Volume']:,}",
            format_large_number(info.get('marketCap', 0)) if info.get('marketCap') else 'N/A',
            f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else 'N/A',
            f"${info.get('trailingEps', 0):.2f}" if info.get('trailingEps') else 'N/A',
            f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A',
            f"{info.get('beta', 0):.2f}" if info.get('beta') else 'N/A',
            f"${info.get('fiftyTwoWeekHigh', 0):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
            f"${info.get('fiftyTwoWeekLow', 0):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A',
            f"{info.get('averageVolume', 0):,}" if info.get('averageVolume') else 'N/A'
        ]
    }
    
    return pd.DataFrame(summary_data)

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">📈 Stock Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("Stock Configuration")
    
    # Stock symbol input
    symbol = st.sidebar.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        help="Enter a valid stock symbol (e.g., AAPL, GOOGL, MSFT)"
    ).upper()
    
    # Time period selection
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }
    
    selected_period = st.sidebar.selectbox(
        "Select Time Period",
        options=list(period_options.keys()),
        index=3
    )
    
    period = period_options[selected_period]
    
    # Chart type selection
    chart_type = st.sidebar.selectbox(
        "Chart Type",
        options=["candlestick", "line"],
        index=0
    )
    
    # Fetch data button
    if st.sidebar.button("Analyze Stock", type="primary"):
        if symbol:
            with st.spinner(f"Fetching data for {symbol}..."):
                data, info = get_stock_data(symbol, period)
                
                if data is not None and not data.empty:
                    # Store data in session state
                    st.session_state['stock_data'] = data
                    st.session_state['stock_info'] = info
                    st.session_state['symbol'] = symbol
                    st.success(f"Data loaded successfully for {symbol}")
                else:
                    st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
        else:
            st.error("Please enter a stock symbol.")
    
    # Display results if data is available
    if 'stock_data' in st.session_state and st.session_state['stock_data'] is not None:
        data = st.session_state['stock_data']
        info = st.session_state['stock_info']
        current_symbol = st.session_state['symbol']
        
        # Current price and company info
        current_price = data['Close'].iloc[-1]
        company_name = info.get('longName', current_symbol) if info else current_symbol
        
        st.subheader(f"{company_name} ({current_symbol})")
        
        # Price display
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Current Price",
                f"${current_price:.2f}",
                f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            last_updated = data.index[-1].strftime("%Y-%m-%d %H:%M")
            st.info(f"Last Updated: {last_updated}")
        
        # Key metrics
        st.subheader("Key Metrics")
        if info:
            display_stock_info(info, current_price)
        
        # Interactive chart
        st.subheader("Price Chart")
        fig = create_stock_chart(data, current_symbol, chart_type)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Financial summary table
        st.subheader("Financial Summary")
        summary_df = create_financial_summary_table(data, info, current_symbol)
        
        if summary_df is not None:
            st.dataframe(summary_df, use_container_width=True)
            
            # CSV download
            csv_buffer = io.StringIO()
            summary_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="Download Summary as CSV",
                data=csv_data,
                file_name=f"{current_symbol}_financial_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        
        # Historical data table
        st.subheader("Historical Data")
        
        # Prepare historical data for display
        historical_display = data.copy()
        historical_display.index = historical_display.index.strftime('%Y-%m-%d')
        historical_display = historical_display.round(2)
        
        st.dataframe(historical_display, use_container_width=True)
        
        # Download historical data
        historical_csv = io.StringIO()
        historical_display.to_csv(historical_csv)
        historical_csv_data = historical_csv.getvalue()
        
        st.download_button(
            label="Download Historical Data as CSV",
            data=historical_csv_data,
            file_name=f"{current_symbol}_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Additional analysis
        with st.expander("Technical Analysis"):
            if len(data) > 50:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Recent performance
                    st.write("**Recent Performance**")
                    returns_1w = ((current_price / data['Close'].iloc[-8]) - 1) * 100
                    returns_1m = ((current_price / data['Close'].iloc[-22]) - 1) * 100
                    
                    st.write(f"1 Week Return: {returns_1w:.2f}%")
                    st.write(f"1 Month Return: {returns_1m:.2f}%")
                
                with col2:
                    # Volatility
                    st.write("**Volatility Analysis**")
                    returns = data['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252) * 100  # Annualized
                    st.write(f"Annual Volatility: {volatility:.2f}%")
                    
                    # Average volume
                    avg_volume_period = data['Volume'].mean()
                    st.write(f"Average Volume ({selected_period}): {avg_volume_period:,.0f}")
            else:
                st.info("More data needed for comprehensive technical analysis.")
    
    else:
        # Welcome message
        st.info("👋 Welcome to the Stock Analysis Dashboard! Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started.")
        
        # Example stocks
        st.subheader("Popular Stocks to Try")
        example_stocks = {
            "AAPL": "Apple Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation"
        }
        
        cols = st.columns(3)
        for i, (ticker, name) in enumerate(example_stocks.items()):
            with cols[i % 3]:
                if st.button(f"{ticker}\n{name}", key=ticker):
                    st.sidebar.text_input("Enter Stock Symbol", value=ticker)
                    st.rerun()

if __name__ == "__main__":
    main()
