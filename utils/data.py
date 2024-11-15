import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Dict, Any

@st.cache_data(ttl=60*15)
def get_stock_data(symbol: str, period: str = "1mo") -> pd.DataFrame:
    try:
        return yf.Ticker(symbol).history(period=period).reset_index()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60*5)
def get_realtime_price(symbol: str) -> Dict[str, Any]:
    try:
        data = yf.Ticker(symbol).fast_info
        return {
            "price": data.last_price,
            "change": data.last_price - data.previous_close,
            "change_percent": (data.last_price - data.previous_close)/data.previous_close*100,
            "status": "success"
        }
    except Exception:
        return {
            "price": 0,
            "status": "error",
            "message": "Price data unavailable"
        }