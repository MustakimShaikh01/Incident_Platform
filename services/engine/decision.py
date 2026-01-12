def decide_action(confidence, auto_fix_allowed, trend):
    if confidence < 0.6:
        return "ANALYZE_ONLY"

    if auto_fix_allowed and trend != "CRITICAL":
        return "REQUEST_APPROVAL"

    return "ASSIST_ONLY"
