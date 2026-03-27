from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from explainer.explain import generate_signal_explanation_from_dict
from signals.merger import merge_signals


app = FastAPI(title="Opportunity Radar Dashboard")
BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard() -> HTMLResponse:
    if not INDEX_PATH.exists():
        return HTMLResponse("<h1>Dashboard UI not found.</h1>", status_code=404)
    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))


from signals.merger import merge_signals

@app.get("/api/signals")
async def get_signals():
    merged_signals = merge_signals()

    enriched_signals = []

    for signal in merged_signals:
        score = signal.get("conviction_score", 0)

        # Convert score → label
        if score >= 8:
            conviction = "Strong"
        elif score >= 5:
            conviction = "Moderate"
        else:
            conviction = "Weak"

        enriched_signals.append({
            "symbol": signal.get("symbol"),
            "signal_types_combined": signal.get("signal_types_combined"),
            "score": score,
            "conviction": conviction,
            "date": signal.get("date"),
            "explanation": generate_signal_explanation_from_dict(signal)
        })

    # Sort (highest score first)
    enriched_signals.sort(
        key=lambda x: (x["score"], x["date"]),
        reverse=True
    )

    return {"signals": enriched_signals}