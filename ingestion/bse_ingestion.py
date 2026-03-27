import sqlite3
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime

DB_DIR = "db"
DB_PATH = f"{DB_DIR}/radar.db"

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            trade_type TEXT, -- 'BULK_DEAL' or 'INSIDER_BUY'
            value_in_rs REAL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def fetch_bse_data():
    print(f"[{datetime.now()}] Fetching BSE data...")
    headers = {
        "Referer": "https://www.bseindia.com/",
        "User-Agent": "Mozilla/5.0"
    }
    
    # In a real scenario, use requests.get() to hit BSE endpoints:
    # URL 1: https://api.bseindia.com/BseIndiaAPI/api/BulkBlockDeal/w
    # URL 2: https://api.bseindia.com/BseIndiaAPI/api/InsiderTrade/w
    
    # For hackathon/demo purposes, we seed db with initial data if empty
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trades")
    if cursor.fetchone()[0] == 0:
        print("Seeding database with demo market data...")
        cursor.executemany("""
            INSERT INTO trades (company_name, trade_type, value_in_rs, details)
            VALUES (?, ?, ?, ?)
        """, [
            ("Reliance Ind", "BULK_DEAL", 150000000, "Block deal by institutional investor"),
            ("HDFC Bank", "INSIDER_BUY", 6000000, "Promoter buying shares off-market"),
            ("TCS", "BULK_DEAL", 50000000, "Minor block deal, below threshold"),
            ("Adani Ent", "INSIDER_BUY", 4000000, "Small insider buy, below threshold")
        ])
        conn.commit()
    conn.close()

def run_ingestion():
    init_db()
    fetch_bse_data() # Initial run before scheduler ticks
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_bse_data, 'interval', minutes=15)
    scheduler.start()
    return scheduler
