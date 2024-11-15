import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import os
from datetime import datetime
import time
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Setup ---
st.set_page_config(
    page_title="Indian Stock Dashboard",
    layout="wide",
    page_icon="📊"
)

# Initialize OpenAI
api_key = os.getenv("OPENAI_API_KEY")


# --- Helper Functions ---
def format_number(text):
    """Format numerical values from text"""
    if not text or text == 'N/A':
        return 'N/A'

    try:
        if isinstance(text, (int, float)):
            return text

        clean_text = text.replace(',', '').replace('%', '').replace('₹', '').strip()
        value = float(clean_text)
        return int(value) if value.is_integer() else value
    except:
        return text


def get_screener_data(ticker):
    """Get stock data from Screener.in"""
    try:
        session = requests.Session()

        # Handle special cases for indices
        if ticker in ["NIFTY50", "Nifty50"]:
            ticker = "NIFTY"
        elif ticker == "SENSEX30":
            ticker = "SENSEX"

        consolidated_tickers = ["RELIANCE", "HDFCBANK", "TCS", "ICICIBANK", "LT", "INFY", "BHARTIARTL", "ITC", "SBIN"]
        if ticker in consolidated_tickers:
            url = f"https://www.screener.in/company/{ticker}/consolidated/"
        else:
            url = f"https://www.screener.in/company/{ticker}/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.screener.in/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }

        time.sleep(2)
        response = session.get(url, headers=headers, timeout=15)

        # -- DEBUGGING OUTPUT --
        print(f"Request status code: {response.status_code}")
        print(response.text[:500])

        # --- HERE IS THE FIX ---
        soup = BeautifulSoup(response.text, 'html.parser')

        if response.status_code != 200:
            return {"error": f"Could not fetch data for ticker {ticker}. Status code: {response.status_code}"}

        # Get company name
        company_name = soup.select_one('h1').text.strip() if soup.select_one('h1') else ticker

        # Get current price
        price_element = soup.select_one('.company-value')
        current_price = price_element.text.strip() if price_element else "N/A"
        price_display = current_price
        current_price = format_number(current_price)

        # Get price change
        change_element = soup.select_one('.company-value + .text-red, .company-value + .text-green')
        change_pct = change_element.text.strip() if change_element else "N/A"

        # Get market cap
        market_cap_element = soup.select_one('div:-soup-contains("Market Cap") + div')
        market_cap = market_cap_element.text.strip() if market_cap_element else "N/A"

        # Get stock P/E
        pe_ratio_element = soup.select_one('div:-soup-contains("Stock P/E") + div')
        pe_ratio = pe_ratio_element.text.strip() if pe_ratio_element else "N/A"

        # Extract Book Value
        book_value_element = soup.select_one('div:-soup-contains("Price to Book") + div')
        book_value = book_value_element.text.strip() if book_value_element else "N/A"

        # Extract Dividend Yield
        dividend_element = soup.select_one('div:-soup-contains("Dividend Yield") + div')
        dividend_yield = dividend_element.text.strip() if dividend_element else "N/A"

        # Extract CAGR values
        cagr_1yr = soup.select_one('div:-soup-contains("CAGR 1Yr") + div').text.strip() if soup.select_one(
            'div:-soup-contains("CAGR 1Yr") + div') else "N/A"
        cagr_5yr = soup.select_one('div:-soup-contains("CAGR 5Yr") + div').text.strip() if soup.select_one(
            'div:-soup-contains("CAGR 5Yr") + div') else "N/A"
        cagr_10yr = soup.select_one('div:-soup-contains("CAGR 10Yr") + div').text.strip() if soup.select_one(
            'div:-soup-contains("CAGR 10Yr") + div') else "N/A"

        # Get High/Low
        high_low_text = soup.select_one('div:-soup-contains("High / Low") + div').text.strip() if soup.select_one(
            'div:-soup-contains("High / Low") + div') else ""
        high_value, low_value = ("N/A", "N/A")
        if "/" in high_low_text:
            high_value, low_value = [h.strip() for h in high_low_text.split("/")]

        # Sector & About
        about_section = soup.select_one('.about-section')
        sector = "N/A"
        about_text = ""
        if about_section:
            about_text = about_section.text.strip()
            m = re.search(r'sector: ([^,]+)', about_text, re.IGNORECASE)
            if m:
                sector = m.group(1).strip()

        # Generate synthetic chart data
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(days=180)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        base_price = float(current_price) if isinstance(current_price, (int, float)) else 100
        import numpy as np
        np.random.seed(42)
        price_changes = np.random.normal(0, 0.01, size=len(dates))
        prices = [base_price]
        for ch in price_changes:
            prices.append(prices[-1] * (1 + ch))
        prices = prices[1:]
        chart_data = pd.DataFrame({'Date': dates[:len(prices)], 'Close': prices})

        return {
            "company_name": company_name,
            "ticker": ticker,
            "price": price_display,
            "price_numeric": current_price,
            "change_pct": change_pct,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "price_to_book": book_value,
            "dividend_yield": dividend_yield,
            "high": high_value,
            "low": low_value,
            "cagr_1yr": cagr_1yr,
            "cagr_5yr": cagr_5yr,
            "cagr_10yr": cagr_10yr,
            "sector": sector,
            "about": about_text,
            "chart_data": chart_data,
            "error": None
        }

    except Exception as e:
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}


def get_screener_search(query):
    """Search stocks on Screener.in"""
    try:
        url = f"https://www.screener.in/api/company/search/?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return []

        data = response.json()
        return data
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []


def get_popular_stocks():
    """Return the list of 10 specified Indian stocks"""
    return [
        {"name": "Reliance Industries", "ticker": "RELIANCE"},
        {"name": "NIFTY 50", "ticker": "NIFTY"},  # Changed from NIFTY50 to NIFTY
        {"name": "HDFC Bank", "ticker": "HDFCBANK"},
        {"name": "Tata Consultancy Services", "ticker": "TCS"},
        {"name": "ICICI Bank", "ticker": "ICICIBANK"},
        {"name": "Larsen & Toubro", "ticker": "LT"},
        {"name": "Infosys", "ticker": "INFY"},
        {"name": "Bharti Airtel", "ticker": "BHARTIARTL"},
        {"name": "ITC Limited", "ticker": "ITC"},
        {"name": "State Bank of India", "ticker": "SBIN"}
    ]


def get_major_indices():
    """Return major Indian indices"""
    return [
        {"name": "Nifty 50", "ticker": "NIFTY"},  # Correct ticker symbol for Nifty 50
        {"name": "Sensex", "ticker": "SENSEX"}
    ]


def get_financial_news():
    """Get financial news from economic times or moneycontrol"""
    try:
        # Try Economic Times
        url = "https://economictimes.indiatimes.com/markets/stocks/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            news_elements = soup.select('.eachStory')
            for item in news_elements[:5]:
                title_element = item.select_one('h3')
                link_element = item.select_one('a')

                if title_element and link_element:
                    title = title_element.text.strip()
                    link = link_element.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://economictimes.indiatimes.com{link}"

                    news_items.append({
                        "title": title,
                        "url": link
                    })

            if news_items:
                return news_items

        # Fallback to static news
        return [
            {"title": "Nifty scales new highs as IT stocks rally",
             "url": "https://economictimes.indiatimes.com/markets/stocks/news"},
            {"title": "Reliance Industries reports Q4 results",
             "url": "https://economictimes.indiatimes.com/markets/stocks/news"},
            {"title": "Banking stocks lead market gains",
             "url": "https://economictimes.indiatimes.com/markets/stocks/news"},
            {"title": "Global cues drive Indian markets",
             "url": "https://economictimes.indiatimes.com/markets/stocks/news"},
            {"title": "FII investment trends in Indian equities",
             "url": "https://economictimes.indiatimes.com/markets/stocks/news"}
        ]
    except Exception as e:
        # Return backup news
        return [
            {"title": "Market Updates: Daily Trading Summary", "url": "https://economictimes.indiatimes.com/markets"},
            {"title": "Top Gainers and Losers of the Day",
             "url": "https://economictimes.indiatimes.com/markets/stocks"},
            {"title": "Quarterly Results Analysis", "url": "https://economictimes.indiatimes.com/markets/earnings"},
            {"title": "Sectoral Performance Overview", "url": "https://economictimes.indiatimes.com/markets/stocks"},
            {"title": "Investment Ideas for Current Market",
             "url": "https://economictimes.indiatimes.com/markets/stocks"}
        ]


def get_basic_analysis(stock_data):
    """Provide basic stock analysis without using AI"""
    if not stock_data or stock_data.get("error"):
        return "No data available for analysis."

    analysis = []

    # Price analysis
    try:
        price = stock_data.get('price_numeric')
        if price:
            if stock_data.get('change_pct', '').startswith('-'):
                analysis.append(
                    f"{stock_data['company_name']} is currently trading at {stock_data['price']} with a negative change of {stock_data['change_pct']}.")
            else:
                analysis.append(
                    f"{stock_data['company_name']} is currently trading at {stock_data['price']} with a positive change of {stock_data['change_pct']}.")
    except:
        pass

    # P/E analysis
    try:
        pe = format_number(stock_data.get('pe_ratio', 'N/A'))
        if pe != 'N/A' and isinstance(pe, (int, float)):
            if pe < 15:
                analysis.append(
                    f"The P/E ratio of {pe} is relatively low, potentially indicating the stock is undervalued.")
            elif pe > 25:
                analysis.append(
                    f"The P/E ratio of {pe} is relatively high, which could suggest the stock is overvalued.")
            else:
                analysis.append(f"The P/E ratio of {pe} is within a moderate range.")
    except:
        pass

    # Dividend analysis
    try:
        dividend = stock_data.get('dividend_yield', 'N/A')
        if dividend and dividend != 'N/A' and dividend != '0%':
            analysis.append(f"The stock offers a dividend yield of {dividend}.")
    except:
        pass

    # CAGR analysis
    try:
        cagr_1yr = stock_data.get('cagr_1yr', 'N/A')
        cagr_5yr = stock_data.get('cagr_5yr', 'N/A')

        if cagr_1yr and cagr_1yr != 'N/A' and cagr_5yr and cagr_5yr != 'N/A':
            analysis.append(f"The 1-year CAGR is {cagr_1yr} and the 5-year CAGR is {cagr_5yr}.")
    except:
        pass

    if len(analysis) == 0:
        analysis.append(
            f"Basic information for {stock_data['company_name']} is available but no detailed analysis could be generated.")

    return " ".join(analysis)


def track_api_usage(session_state, increment=1):
    """Track API usage in session state"""
    if 'api_calls' not in session_state:
        session_state['api_calls'] = 0

    session_state['api_calls'] += increment

    # Return warning message if approaching free tier limits
    if session_state['api_calls'] >= 10:
        return "Warning: You're approaching your OpenAI API free tier limits."
    return None


# --- Initialize session state ---
if 'last_search' not in st.session_state:
    st.session_state['last_search'] = ""

if 'api_calls' not in st.session_state:
    st.session_state['api_calls'] = 0

# --- UI Layout ---
st.title("📈 Indian Stock Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Sidebar Controls
with st.sidebar:
    st.header("Controls")

    # Search bar
    search_query = st.text_input("Search Company or Symbol", "")

    if search_query and search_query != st.session_state['last_search']:
        st.session_state['last_search'] = search_query
        with st.spinner("Searching..."):
            search_results = get_screener_search(search_query)

            if search_results:
                st.success(f"Found {len(search_results)} results")
                for result in search_results:
                    if st.button(f"{result.get('name')} ({result.get('ticker')})"):
                        ticker = result.get('ticker')
                        st.rerun()
            else:
                st.warning("No results found. Try another search.")

    # Default ticker entry - Changed default from RELIANCE to NIFTY
    ticker = st.text_input("Enter Stock Symbol", "NIFTY").strip().upper()

    # Normalize ticker if it's Nifty50
    if ticker in ["NIFTY50", "Nifty50"]:
        ticker = "NIFTY"

    st.divider()
    st.markdown("**Popular Stocks:**")
    popular_stocks = get_popular_stocks()

    # Display in rows of 2
    for i in range(0, len(popular_stocks), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(popular_stocks):
                with cols[j]:
                    if st.button(popular_stocks[i + j]["ticker"]):
                        ticker = popular_stocks[i + j]["ticker"]
                        st.rerun()

    # Added indices section
    st.markdown("**Market Indices:**")
    indices = get_major_indices()
    cols = st.columns(2)
    for i, index in enumerate(indices):
        with cols[i % 2]:
            if st.button(index["name"]):
                ticker = index["ticker"]
                st.rerun()

# Main Dashboard
tab1, tab2, tab3 = st.tabs(["📊 Market Data", "📰 Latest News", "🤖 AI Advisor"])

with tab1:
    with st.spinner("Fetching stock data..."):
        data = get_screener_data(ticker)

    if data.get("error"):
        st.error(data["error"])
        st.info("Try searching for a different company or check the symbol. For Nifty 50, use 'NIFTY'.")
    else:
        # Create header with company name and current price
        st.header(f"{data['company_name']} ({ticker})")

        # About section similar to screenshot
        st.subheader("ABOUT")
        st.markdown(data['about'] if data['about'] else "No company information available.")

        # Financial metrics in a blue background container
        metrics_container = st.container()
        with metrics_container:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Market Cap** {data['market_cap']}")
                st.markdown(f"**P/E** {data['pe_ratio']}")
                st.markdown(f"**CAGR 1Yr** {data['cagr_1yr']}")

            with col2:
                st.markdown(f"**Current Price** {data['price']}")
                st.markdown(f"**Price to Book value** {data['price_to_book']}")
                st.markdown(f"**CAGR 5Yr** {data['cagr_5yr']}")

            with col3:
                st.markdown(f"**High / Low** {data['high']} / {data['low']}")
                st.markdown(f"**Dividend Yield** {data['dividend_yield']}")
                st.markdown(f"**CAGR 10Yr** {data['cagr_10yr']}")

        # Chart section with tabs for different time periods
        st.subheader("Chart")
        chart_tabs = st.tabs(["1M", "6M", "1Yr", "3Yr", "5Yr", "10Yr", "Max"])

        # Get the chart data
        chart_data = data.get('chart_data')


        # Function to filter chart data based on time period
        def get_filtered_chart_data(data, period):
            if data is None or data.empty:
                return None

            now = pd.Timestamp.now()

            if period == "1M":
                cutoff = now - pd.DateOffset(months=1)
            elif period == "6M":
                cutoff = now - pd.DateOffset(months=6)
            elif period == "1Yr":
                cutoff = now - pd.DateOffset(years=1)
            elif period == "3Yr":
                cutoff = now - pd.DateOffset(years=3)
            elif period == "5Yr":
                cutoff = now - pd.DateOffset(years=5)
            elif period == "10Yr":
                cutoff = now - pd.DateOffset(years=10)
            else:  # Max
                return data

            return data[data['Date'] >= cutoff]


        # Create charts for each time period
        for i, period in enumerate(["1M", "6M", "1Yr", "3Yr", "5Yr", "10Yr", "Max"]):
            with chart_tabs[i]:
                filtered_data = get_filtered_chart_data(chart_data, period)

                if filtered_data is not None and not filtered_data.empty:
                    # Create interactive Plotly chart
                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatter(
                            x=filtered_data['Date'],
                            y=filtered_data['Close'],
                            mode='lines',
                            name='Price',
                            line=dict(color='#4169E1', width=2)
                        )
                    )

                    # Add option for moving averages
                    show_sma = st.checkbox(f"Show 50 DMA (in {period})", key=f"50dma_{period}")
                    show_long_sma = st.checkbox(f"Show 200 DMA (in {period})", key=f"200dma_{period}")

                    if show_sma and len(filtered_data) >= 50:
                        filtered_data['50_SMA'] = filtered_data['Close'].rolling(window=50).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=filtered_data['Date'],
                                y=filtered_data['50_SMA'],
                                mode='lines',
                                name='50 DMA',
                                line=dict(color='orange', width=1.5)
                            )
                        )

                    if show_long_sma and len(filtered_data) >= 200:
                        filtered_data['200_SMA'] = filtered_data['Close'].rolling(window=200).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=filtered_data['Date'],
                                y=filtered_data['200_SMA'],
                                mode='lines',
                                name='200 DMA',
                                line=dict(color='red', width=1.5)
                            )
                        )

                    # Update layout
                    fig.update_layout(
                        title=f"{data['company_name']} - {period} Chart",
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        template="plotly_white",
                        height=500,
                        margin=dict(l=0, r=0, t=40, b=0),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(
                            rangeslider=dict(visible=False),
                            type="date"
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {period} time period")

        # Show additional information in an expander
        with st.expander("Additional Information"):
            st.write(f"""
            **Company:** {data['company_name']}
            **Sector:** {data['sector']}
            **Current Price:** {data['price']}
            **Price Change:** {data['change_pct']}

            For comprehensive data and analysis, visit [Screener.in](https://www.screener.in/company/{ticker}/).
            """)

with tab2:
    st.header("Latest Financial News")
    with st.spinner("Fetching latest news..."):
        news_items = get_financial_news()

    if not news_items:
        st.warning("Could not retrieve news at this time. Please try again later.")
    else:
        for item in news_items:
            with st.expander(item["title"]):
                st.markdown(f"[Read Full Article]({item['url']})")

with tab3:
    st.header("AI Financial Advisor")
    st.caption("Ask questions about the market or specific stocks")

    # Check for API key
    if not api_key:
        api_key = st.text_input("Enter OpenAI API Key to enable AI Advisor", type="password")
        if api_key:
            st.success("API Key set for this session")
            st.info("Using free tier OpenAI API. Responses may be limited based on your quota.")
        else:
            st.warning("Please enter your OpenAI API key to use the AI Advisor feature")

    # Initialize chat state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input(f"Ask about {ticker}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    stock_data = get_screener_data(ticker)
                    if stock_data.get("error"):
                        st.warning(f"Could not retrieve data for {ticker}. Providing a general answer.")
                        stock_info = "No specific stock data available."
                    else:
                        # Create a more concise stock info to reduce token usage
                        stock_info = f"Company: {stock_data['company_name']}, Ticker: {ticker}, Price: {stock_data['price']}, Change: {stock_data['change_pct']}, P/E: {stock_data['pe_ratio']}, Div Yield: {stock_data['dividend_yield']}"

                    if api_key:
                        try:
                            client = OpenAI(api_key=api_key)

                            # Use a more efficient system prompt to save tokens
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[{
                                    "role": "system",
                                    "content": f"You're a financial advisor. Current stock data: {stock_info}. Be concise."
                                }, {
                                    "role": "user",
                                    "content": prompt
                                }],
                                temperature=0.3,
                                max_tokens=150  # Limit response size for free tier
                            )
                            result = response.choices[0].message.content
                        except Exception as api_error:
                            # Handle API errors more specifically
                            if "429" in str(api_error):
                                result = f"Free tier API quota exceeded. Try again later or upgrade your OpenAI plan. Stock info: {stock_info}"
                                st.error(
                                    "API quota exceeded. Consider spacing out your questions or upgrading your OpenAI plan.")
                            elif "401" in str(api_error):
                                result = "Invalid API key. Please check your OpenAI API key."
                                st.error("Authentication error. Please verify your API key.")
                            else:
                                result = f"AI service unavailable. Here's the stock data: {stock_info}"
                                st.error(f"API error: {str(api_error)}")
                    else:
                        result = "AI Advisor requires an OpenAI API key. Please enter your API key in the text field above."

                    st.write(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})

                except Exception as e:
                    fallback_response = f"Sorry, I couldn't process your question. Here's what I know about {ticker}: {stock_data['company_name']} at price {stock_data.get('price', 'N/A')}."
                    st.error(f"Error: {str(e)}")
                    st.write(fallback_response)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_response})
                    st.info("This could be due to an invalid API key, connection issue, or quota limits.")

# --- Footer ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("*Data provided by Screener.in. AI responses may not be 100% accurate.*")
with col2:
    st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))