import json, os
from datetime import datetime

STATS_FILE = "state/error_stats.json"

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE) as f:
        return json.load(f)

def update_stats(error_type):
    stats = load_stats()
    entry = stats.get(error_type, {"count": 0})
    entry["count"] += 1
    entry["last_seen"] = datetime.utcnow().isoformat()
    stats[error_type] = entry

    os.makedirs("state", exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    return entry

def classify_trend(count):
    if count >= 20:
        return "CRITICAL"
    if count >= 5:
        return "REPEATED"
    return "OCCASIONAL"
