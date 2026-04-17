from typing import List

SYMPTOM_SCORES = {
    "headache":    30,
    "bleeding":    50,
    "swelling":    40,
    "no_movement": 45,
    "weakness":    20,
    "dizziness":   20,
    "nausea":      10,
}

def calculate_risk(symptoms: List[str], missed_doses: int) -> dict:
    score = 0
    matched = []

    for symptom in symptoms:
        if symptom in SYMPTOM_SCORES:
            score += SYMPTOM_SCORES[symptom]
            matched.append(symptom)

    score += missed_doses * 15
    score = min(score, 100)

    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    reason_parts = []
    if matched:
        reason_parts.append(f"Symptoms: {', '.join(matched)}")
    if missed_doses > 0:
        reason_parts.append(f"Missed {missed_doses} dose(s)")

    return {
        "score":      score,
        "risk_level": risk_level,
        "reason":     " | ".join(reason_parts) if reason_parts else "All checks normal"
    }