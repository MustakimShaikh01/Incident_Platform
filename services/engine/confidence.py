def calculate_confidence(error_type, stacktrace, seen_before):
    score = 0.0

    if error_type:
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
