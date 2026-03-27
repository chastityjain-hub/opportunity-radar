def assign_score(signal: dict) -> int:
    """
    Assigns a conviction score 1-10 based on value and signal type.
    """
    score = 1
    val = signal.get("value_in_rs", 0)
    trade_type = signal.get("trade_type", "")
    
    if trade_type == "INSIDER_BUY":
        score = 5 # Base score
        if val > 50000000:     # > 5 Crore
            score += 3
        elif val > 10000000:   # > 1 Crore
            score += 2
        else:
            score += 1
            
    elif trade_type == "BULK_DEAL":
        score = 3 # Base score
        if val > 500000000:    # > 50 Crore
            score += 5
        elif val > 200000000:  # > 20 Crore
            score += 3
        elif val > 100000000:  # > 10 Crore
            score += 1
            
    return min(10, max(1, score))

def score_signals(signals: list) -> list:
    for sig in signals:
        sig["score"] = assign_score(sig)
    # Sort descending by assigned score
    return sorted(signals, key=lambda x: x["score"], reverse=True)
