import streamlit as st
from chatbot import IntelligentInvestorChatbot
from utils.data import get_stock_data, get_realtime_price
from utils.news import get_finance_news
import time

# Configure page
st.set_page_config(page_title="Finance Assistant", layout="wide")

# Initialize chatbot once
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = IntelligentInvestorChatbot()

# Sidebar controls
st.sidebar.title("Controls")
symbol = st.sidebar.text_input("Stock Symbol", "AAPL")
timeframe = st.sidebar.selectbox("Timeframe", ["1d", "1wk", "1mo"])

# Main dashboard
st.title("📈 Smart Finance Assistant")

# Real-time Data Section
col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    st.subheader("Live Prices")
    if symbol:
        price_data = get_realtime_price(symbol)
        if price_data["status"] == "success":
            st.metric("Current Price", f"${price_data['price']:.2f}",
                      f"{price_data['change_percent']:.2f}%")

with col2:
    st.subheader("Market News")
    news_items = get_finance_news(symbol)
    for item in news_items[:3]:
        st.markdown(f"» [{item['title']}]({item['link']})")

# Historical Data Chart
with col3:
    st.subheader("Historical Trend")
    data = get_stock_data(symbol, timeframe)
    if not data.empty:
        st.line_chart(data.set_index('Date')['Close'])

# Chatbot Interface
st.divider()
st.subheader("💬 Intelligent Investment Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about investing or stock analysis"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.chatbot.respond(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})