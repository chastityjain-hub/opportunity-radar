from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

from signals.rules import get_significant_signals
from scoring.scorer import score_signals
from explainer.explain import generate_signal_explanation

app = FastAPI(title="Opportunity Radar Dashboard")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard UI not found. Check index.html</h1>"

@app.get("/api/signals")
async def get_signals():
    # 1. Fetch from DB
    raw_signals = get_significant_signals()
    
    # 2. Score them
    ranked_signals = score_signals(raw_signals)
    
    # 3. Add Explanations & Sentiment via LLM
    for sig in ranked_signals:
        if "explanation" not in sig or not sig.get("explanation"):
            result = generate_signal_explanation(sig)
            sig["explanation"] = result["text"]
            sig["sentiment"] = result["sentiment"]
            
    return {"signals": ranked_signals}
