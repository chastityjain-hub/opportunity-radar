import sqlite3
import os

DB_PATH = "db/radar.db"

def get_significant_signals():
    """
    Detects bulk deals over Rs 10 crore and insider buys over Rs 50 lakh.
    """
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 10 Crore = 100,000,000
    # 50 Lakh  = 5,000,000
    query = """
        SELECT id, company_name, trade_type, value_in_rs, details, timestamp
        FROM trades
        WHERE 
            (trade_type = 'BULK_DEAL' AND value_in_rs > 100000000)
            OR 
            (trade_type = 'INSIDER_BUY' AND value_in_rs > 5000000)
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        signals = []
        for row in rows:
            signals.append({
                "id": row[0],
                "company_name": row[1],
                "trade_type": row[2],
                "value_in_rs": row[3],
                "details": row[4],
                "timestamp": row[5]
            })
        return signals
    except Exception as e:
        print(f"Error fetching signals: {e}")
        return []
    finally:
        conn.close()
