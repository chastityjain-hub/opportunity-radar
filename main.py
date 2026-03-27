import uvicorn
from ingestion.bse_ingestion import run_ingestion
from dashboard.main import app

if __name__ == "__main__":
    print("🚀 Initializing Opportunity Radar...")
    
    # 1. Initialize SQLite Database & start the apscheduler background task
    scheduler = run_ingestion()
    print("✅ BSE Ingestion scheduler started (Runs every 15 mins).")

    # 2. Start Dashboard
    print("🌐 Starting FastAPI dashboard at http://localhost:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
