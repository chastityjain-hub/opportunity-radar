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


@app.get("/api/signals")
async def get_signals() -> dict[str, list[dict[str, object]]]:
    merged_signals = merge_signals()

    enriched_signals: list[dict[str, object]] = []
    for signal in merged_signals:
        enriched_signals.append(
            {
                "symbol": signal["symbol"],
                "signal_types_combined": signal["signal_types_combined"],
                "strength": signal["strength"],
                "conviction_score": signal["conviction_score"],
                "date": signal["date"],
                "explanation": generate_signal_explanation_from_dict(signal),
            }
        )

    enriched_signals.sort(
        key=lambda item: (
            int(item["conviction_score"]),
            str(item["date"]),
            str(item["symbol"]),
        ),
        reverse=True,
    )
    return {"signals": enriched_signals}
