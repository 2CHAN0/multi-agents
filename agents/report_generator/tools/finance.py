"""
Finance Tools
=============
Retrieves financial data such as exchange rates using yfinance.
"""

import yfinance as yf
from typing import Any
from langchain.tools import tool


@tool
def get_exchange_rate(target_currency: str, base_currency: str = "USD") -> dict[str, Any]:
    """
    Get the current exchange rate between two currencies.
    
    Args:
        target_currency: The currency to convert TO (e.g., 'KRW', 'EUR').
        base_currency: The currency to convert FROM (default: 'USD').
        
    Returns:
        A dictionary containing the exchange rate and metadata.
    """
    # Yahoo Finance symbol format
    if base_currency.upper() == "USD":
        symbol = f"{target_currency.upper()}=X"
    else:
        symbol = f"{base_currency.upper()}{target_currency.upper()}=X"

    try:
        ticker = yf.Ticker(symbol)
        # fast_info is often faster/more reliable for current price than history
        price = ticker.fast_info.get('last_price')
        
        if price is None:
             # Fallback to history
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
        
        if price is None:
            return {
                "error": f"Could not fetch rate for {symbol}",
                "success": False
            }
            
        return {
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "rate": price,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

