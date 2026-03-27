# Opportunity Radar

Opportunity Radar is an AI-powered signal detection system for Indian retail investors.  
It identifies unusual market activity and converts raw data into simple, actionable insights.

Built for ET AI Hackathon 2026.

---

## Problem

Most retail investors rely on news, tips, or social media to make decisions.  
However, important signals like large trades or unusual activity are hidden in raw data and are difficult to interpret.

---

## Solution

Opportunity Radar detects meaningful patterns in market data and presents them in a clear and structured way.

It focuses on:
- unusual trading activity  
- statistical anomalies  
- signal confirmation using multiple indicators  
- simple explanations for non-expert users  

---

## How It Works

1. Data Ingestion  
   Market data is fetched using yfinance and stored in a local SQLite database.

2. Signal Detection  
   The system detects:
   - high trading volume  
   - large transaction values  

3. Anomaly Detection  
   Z-score is used to identify activity that deviates from historical patterns.

4. Signal Merging  
   Multiple signals are combined to produce higher-confidence outputs.  
   Each signal is assigned a conviction score.

5. AI Explanation  
   A language model generates a short explanation describing:
   - what happened  
   - why it matters  
   - what to watch next  

---

## Example Output


Stock: TCS.NS
Signal: large_deal_value + zscore_anomaly
Conviction: Moderate (6/10)

Insight:
Unusually large trades combined with statistical anomaly suggest possible accumulation. Monitor price movement and upcoming disclosures.


---

## Tech Stack

- Python 3.12  
- FastAPI  
- SQLite  
- Pandas and NumPy  
- yfinance  
- Google Gemini (LLM)  

---

## How to Run

Install dependencies:


pip install -r requirements.txt


Run the pipeline:


python -m ingestion.bse_ingestion
python -m signals.merger
python -m explainer.explain


---

## Key Features

- Detects unusual market activity  
- Uses statistical methods to filter noise  
- Combines multiple signals for better accuracy  
- Generates simple, readable explanations  

---

## Future Improvements

- Live NSE/BSE data integration  
- Web dashboard  
- Alerts and notifications  
- Portfolio tracking  

---

## Author

Chastity Jain  
https://github.com/chastityjain-hub