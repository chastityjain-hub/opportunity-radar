import sys
import os

# Ensure the root directory logic is properly aligned 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm import get_llm_explanation

def generate_signal_explanation(signal: dict) -> dict:
    """
    Calls llm.py to generate plain-English explanation and exact market sentiment tag.
    """
    company = signal.get("company_name", "Unknown")
    trade_type = signal.get("trade_type", "TRADE")
    value = signal.get("value_in_rs", 0)
    
    # Format value nicely for prompt context
    if value >= 10000000:
        val_str = f"Rs {value / 10000000:.2f} Crore"
    else:
        val_str = f"Rs {value / 100000:.2f} Lakh"
        
    prompt = f"""
    You are a financial analyst specializing in Indian stock markets.
    Analyze this signal and explain it in simple English for a retail investor.
    Keep it strictly to 2-3 sentences max. Don't use heavy jargon without brief context.
    
    Company: {company}
    Event: {trade_type}
    Value: {val_str}
    
    Explain what this implies for the stock.
    Finally, append a sentiment tag on a new line exactly like this: 
    SENTIMENT: BULLISH (or BEARISH or NEUTRAL).
    """
    
    raw_response = get_llm_explanation(prompt)
    
    # Parse out sentiment
    sentiment = "NEUTRAL"
    text = raw_response
    
    if "SENTIMENT:" in raw_response:
        parts = raw_response.split("SENTIMENT:")
        text = parts[0].strip()
        s_tag = parts[1].strip().upper()
        if "BULLISH" in s_tag: sentiment = "BULLISH"
        elif "BEARISH" in s_tag: sentiment = "BEARISH"
        else: sentiment = "NEUTRAL"
    else:
        # Fallback keyword search
        up = raw_response.upper()
        if "BULLISH" in up: sentiment = "BULLISH"
        elif "BEARISH" in up: sentiment = "BEARISH"
        
    return {"text": text, "sentiment": sentiment}
