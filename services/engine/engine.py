from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread
import json
import os
from datetime import datetime

app = Flask(__name__)

# -------------------------------------------------
# ERROR KNOWLEDGE BASE (EXTEND THIS, NOT LOGIC)
# -------------------------------------------------

ERROR_CATALOG = {
    # ---------- SAFE AUTO-FIX (Tier 1) ----------
    "ZeroDivisionError": {
        "category": "RUNTIME",
        "risk": "LOW",
        "auto_fix": True,
        "root_cause": "Division by zero occurred during an arithmetic operation.",
        "suggested_fix": [
            "Add a check to ensure divisor is not zero",
            "Raise a clear exception when divisor is zero"
        ]
    },
    "IndexError": {
        "category": "RUNTIME",
        "risk": "LOW",
        "auto_fix": True,
        "root_cause": "Attempted to access an index outside the valid range.",
        "suggested_fix": [
            "Validate index boundaries",
            "Check input size before accessing elements"
        ]
    },
    "KeyError": {
        "category": "RUNTIME",
        "risk": "LOW",
        "auto_fix": True,
        "root_cause": "Dictionary key was accessed but does not exist.",
        "suggested_fix": [
            "Use dict.get() with a default value",
            "Check key existence before access"
        ]
    },
    "TypeError": {
        "category": "RUNTIME",
        "risk": "LOW",
        "auto_fix": True,
        "root_cause": "Operation performed on an incompatible data type.",
        "suggested_fix": [
            "Validate object type before operation",
            "Add explicit type checks"
        ]
    },
    "ValueError": {
        "category": "RUNTIME",
        "risk": "LOW",
        "auto_fix": True,
        "root_cause": "Function received a value of the correct type but invalid value.",
        "suggested_fix": [
            "Validate input values",
            "Add defensive exception handling"
        ]
    },

    # ---------- ASSISTED RESOLUTION (Tier 2) ----------
    "ModuleNotFoundError": {
        "category": "DEPENDENCY",
        "risk": "MEDIUM",
        "auto_fix": False,
        "root_cause": "Required Python module is missing from the environment.",
        "suggested_fix": [
            "Add dependency to requirements.txt",
            "Install the package in the active environment"
        ]
    },
    "ImportError": {
        "category": "DEPENDENCY",
        "risk": "MEDIUM",
        "auto_fix": False,
        "root_cause": "Failed to import a module or symbol.",
        "suggested_fix": [
            "Verify installed package version",
            "Check import paths and names"
        ]
    },
    "FileNotFoundError": {
        "category": "ENVIRONMENT",
        "risk": "MEDIUM",
        "auto_fix": False,
        "root_cause": "Referenced file does not exist at the given path.",
        "suggested_fix": [
            "Verify file path",
            "Create the file if required"
        ]
    },
    "PermissionError": {
        "category": "ENVIRONMENT",
        "risk": "MEDIUM",
        "auto_fix": False,
        "root_cause": "Insufficient permissions to access a file or resource.",
        "suggested_fix": [
            "Check file permissions",
            "Run process with correct access rights"
        ]
    },

    # ---------- ANALYZE ONLY (Tier 3) ----------
    "MemoryError": {
        "category": "SYSTEM",
        "risk": "HIGH",
        "auto_fix": False,
        "root_cause": "Application exhausted available memory.",
        "suggested_fix": [
            "Investigate memory usage",
            "Optimize data structures or processing logic"
        ]
    },
    "RecursionError": {
        "category": "SYSTEM",
        "risk": "HIGH",
        "auto_fix": False,
        "root_cause": "Maximum recursion depth exceeded.",
        "suggested_fix": [
            "Refactor recursive logic",
            "Replace recursion with iteration"
        ]
    }
}

# -------------------------------------------------
# STATE & STORAGE
# -------------------------------------------------

STATE_DIR = "state"
STATS_FILE = os.path.join(STATE_DIR, "error_stats.json")

os.makedirs(STATE_DIR, exist_ok=True)

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
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)
    return entry

def classify_trend(count):
    if count >= 20:
        return "CRITICAL"
    if count >= 5:
        return "REPEATED"
    return "OCCASIONAL"

# -------------------------------------------------
# CONFIDENCE SCORING
# -------------------------------------------------

def calculate_confidence(error_type, stacktrace, seen_before):
    score = 0.0

    if error_type in ERROR_CATALOG:
        score += 0.4
    if stacktrace:
        score += 0.2
    if seen_before:
        score += 0.2
    if error_type in [
        "ZeroDivisionError", "IndexError", "KeyError",
        "TypeError", "ValueError"
    ]:
        score += 0.2

    return round(min(score, 1.0), 2)

# -------------------------------------------------
# VERSION CONFLICT DETECTION
# -------------------------------------------------

LIB_VERSION_RULES = {
    "numpy": {
        "max_python": "3.10",
        "issue": "numpy 2.x may be unstable on Python 3.11"
    }
}

def detect_version_conflicts(runtime):
    conflicts = []
    python_version = runtime.get("python", "")
    libs = runtime.get("libs", {})

    for lib, rule in LIB_VERSION_RULES.items():
        if lib in libs and python_version > rule["max_python"]:
            conflicts.append({
                "library": lib,
                "issue": rule["issue"]
            })
    return conflicts

# -------------------------------------------------
# DECISION ENGINE
# -------------------------------------------------

def decide_action(confidence, auto_fix_allowed, trend):
    if confidence < 0.6:
        return "ANALYZE_ONLY"
    if auto_fix_allowed and trend != "CRITICAL":
        return "REQUEST_APPROVAL"
    return "ASSIST_ONLY"

# -------------------------------------------------
# ASYNC QUEUE PROCESSING
# -------------------------------------------------

incident_queue = Queue()

def process_incident(payload):
    error_type = payload.get("error_type", "")
    message = payload.get("message", "")
    stacktrace = payload.get("stacktrace", [])
    runtime = payload.get("runtime", {})

    stats = update_stats(error_type)
    trend = classify_trend(stats["count"])

    confidence = calculate_confidence(
        error_type,
        stacktrace,
        seen_before=stats["count"] > 1
    )

    conflicts = detect_version_conflicts(runtime)
    error_info = ERROR_CATALOG.get(error_type, {})

    decision = decide_action(
        confidence,
        error_info.get("auto_fix", False),
        trend
    )

    result = {
        "error_type": error_type,
        "category": error_info.get("category", "UNKNOWN"),
        "risk": error_info.get("risk", "HIGH"),
        "confidence": confidence,
        "trend": trend,
        "decision": decision,
        "root_cause": error_info.get("root_cause"),
        "suggested_fix": error_info.get("suggested_fix"),
        "version_conflicts": conflicts,
        "context": {
            "message": message,
            "stacktrace": stacktrace[:5]
        }
    }

    # In real system: email / approval / auto-fix / audit
    print("INCIDENT ANALYSIS RESULT:")
    print(json.dumps(result, indent=2))

def worker():
    while True:
        payload = incident_queue.get()
        if payload is None:
            break
        process_incident(payload)
        incident_queue.task_done()

Thread(target=worker, daemon=True).start()

# -------------------------------------------------
# API ENDPOINT
# -------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.json or {}
    incident_queue.put(payload)
    return jsonify({"status": "QUEUED_FOR_ANALYSIS"})

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
