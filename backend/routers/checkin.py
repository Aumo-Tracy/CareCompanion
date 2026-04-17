from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from routers.auth import get_current_user, require_role
from services.risk_scorer import calculate_risk
from services.notifier import send_sms
from database import supabase
from utils.demo import DEMO_MODE, demo_log

router = APIRouter()

# ── Condition-specific check-in question sets ──────────────────────
# These define what the frontend should ask per condition.
# Frontend calls GET /checkin/questions to know what to render.

CONDITION_QUESTIONS = {
    "diabetes": {
        "symptoms": [
            "extreme_thirst", "blurred_vision", "confusion",
            "weakness", "headache", "nausea"
        ],
        "extra_fields": ["blood_sugar_reading"],
        "medication_label": "insulin or metformin"
    },
    "gestational_diabetes": {
        "symptoms": [
            "no_fetal_movement", "severe_headache", "swelling",
            "blurred_vision", "nausea", "weakness"
        ],
        "extra_fields": ["blood_sugar_reading", "fetal_movement"],
        "medication_label": "diabetes medication"
    },
    "hiv": {
        "symptoms": [
            "fever", "severe_fatigue", "weight_loss",
            "night_sweats", "nausea", "weakness"
        ],
        "extra_fields": ["art_taken"],
        "medication_label": "ART medication"
    },
    "hypertension": {
        "symptoms": [
            "severe_headache", "chest_pain", "nosebleed",
            "dizziness", "blurred_vision", "nausea"
        ],
        "extra_fields": ["bp_reading_systolic", "bp_reading_diastolic"],
        "medication_label": "blood pressure medication"
    },
    "eclampsia": {
        "symptoms": [
            "severe_headache", "blurred_vision", "swelling",
            "no_fetal_movement", "chest_pain", "seizure_signs"
        ],
        "extra_fields": [
            "bp_reading_systolic", "bp_reading_diastolic", "fetal_movement"
        ],
        "medication_label": "prescribed medication"
    },
    "cancer_remission": {
        "symptoms": [
            "new_lump", "unexplained_bleeding", "severe_weight_loss",
            "persistent_pain", "extreme_fatigue", "nausea"
        ],
        "extra_fields": ["energy_level"],
        "medication_label": "oncology medication"
    },
}

# ── Condition-specific risk weights ───────────────────────────────
# Overrides the base scorer for condition-specific danger signs

CONDITION_SYMPTOM_WEIGHTS = {
    "diabetes": {
        "extreme_thirst": 20, "blurred_vision": 30,
        "confusion": 45, "weakness": 20,
        "headache": 15, "nausea": 10,
    },
    "gestational_diabetes": {
        "no_fetal_movement": 50, "severe_headache": 35,
        "swelling": 30, "blurred_vision": 35,
        "nausea": 10, "weakness": 15,
    },
    "hiv": {
        "fever": 30, "severe_fatigue": 25,
        "weight_loss": 35, "night_sweats": 20,
        "nausea": 10, "weakness": 15,
    },
    "hypertension": {
        "severe_headache": 30, "chest_pain": 50,
        "nosebleed": 25, "dizziness": 20,
        "blurred_vision": 30, "nausea": 10,
    },
    "eclampsia": {
        "severe_headache": 35, "blurred_vision": 35,
        "swelling": 30, "no_fetal_movement": 50,
        "chest_pain": 45, "seizure_signs": 60,
    },
    "cancer_remission": {
        "new_lump": 50, "unexplained_bleeding": 45,
        "severe_weight_loss": 40, "persistent_pain": 35,
        "extreme_fatigue": 25, "nausea": 10,
    },
}

# ── Condition-specific response messages ──────────────────────────

CONDITION_MESSAGES = {
    "low": {
        "diabetes":            "You are doing well today. Keep taking your medication and watch your diet.",
        "gestational_diabetes": "Good news — you and baby are doing well. Keep monitoring your blood sugar.",
        "hiv":                 "Well done for checking in. Keep taking your ART every day at the same time.",
        "hypertension":        "Your readings look manageable. Keep taking your medication and reduce salt.",
        "eclampsia":           "Thank you for checking in. Keep resting and stay hydrated.",
        "cancer_remission":    "You are doing well. Keep attending your follow-up appointments.",
    },
    "medium": {
        "diabetes":            "Your readings need attention. Please take your medication now and drink water.",
        "gestational_diabetes": "Some signs need watching. Rest, take your medication, and call your midwife if worse.",
        "hiv":                 "Please take your ART medication now. Missing doses can affect your treatment.",
        "hypertension":        "Your blood pressure needs attention. Take your medication and avoid stress.",
        "eclampsia":           "Some symptoms concern us. Please rest and contact your midwife today.",
        "cancer_remission":    "Some symptoms need attention. Please contact your clinic this week.",
    },
    "high": {
        "diabetes":            "Your readings are very concerning. Take your medication now. Your caregiver and clinic have been notified.",
        "gestational_diabetes": "This is urgent. Please go to the clinic immediately. Your caregiver has been notified.",
        "hiv":                 "This needs urgent attention. Please go to your clinic today. Your caregiver has been notified.",
        "hypertension":        "Your blood pressure is dangerously high. Go to the clinic now. Your caregiver has been notified.",
        "eclampsia":           "This is an emergency. Go to the hospital immediately. Do not wait. Your caregiver has been notified.",
        "cancer_remission":    "New symptoms need immediate attention. Please go to your oncologist now. Your clinic has been notified.",
    },
}


# ── Request model ─────────────────────────────────────────────────

class CheckInRequest(BaseModel):
    symptoms: List[str]
    missed_doses: int
    extra_data: Optional[dict] = {}
    # extra_data carries condition-specific fields:
    # blood_sugar_reading, bp_reading_systolic, fetal_movement etc.


# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/checkin/questions")
def get_questions(user: dict = Depends(require_role("patient"))):
    """
    Returns the check-in question set for this patient's condition.
    Frontend calls this on load to know what to render.
    """
    condition = user.get("condition")
    if not condition or condition not in CONDITION_QUESTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"No check-in questions found for condition: {condition}"
        )
    return {
        "condition": condition,
        "questions": CONDITION_QUESTIONS[condition]
    }


@router.post("/checkin")
def submit_checkin(
    data: CheckInRequest,
    user: dict = Depends(require_role("patient"))
):
    condition = user.get("condition", "diabetes")
    weights   = CONDITION_SYMPTOM_WEIGHTS.get(condition, {})

    # Score using condition-specific weights
    score   = 0
    matched = []
    for symptom in data.symptoms:
        points = weights.get(symptom, 10)
        score += points
        matched.append(symptom)

    score += data.missed_doses * 15
    score  = min(score, 100)

    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    reason_parts = []
    if matched:
        reason_parts.append(f"Symptoms: {', '.join(matched)}")
    if data.missed_doses > 0:
        reason_parts.append(f"Missed {data.missed_doses} dose(s)")

    reason = " | ".join(reason_parts) if reason_parts else "All clear"

    # Save to Supabase
    supabase.table("checkins").insert({
        "patient_id":  user["id"],
        "symptoms":    data.symptoms,
        "missed_doses": data.missed_doses,
        "extra_data":  data.extra_data,
        "risk_level":  risk_level,
        "risk_score":  score,
        "condition":   condition,
    }).execute()

    # Fire alerts on MEDIUM and HIGH
    if risk_level in ("MEDIUM", "HIGH"):
        _fire_alert(user, risk_level, reason, condition)

    message = CONDITION_MESSAGES[risk_level.lower()][condition]

    demo_log("Check-in", {
        "patient":    user["full_name"],
        "condition":  condition,
        "risk_level": risk_level,
        "score":      score,
        "reason":     reason
    })

    return {
        "patient":    user["full_name"],
        "condition":  condition,
        "risk_level": risk_level,
        "risk_score": score,
        "reason":     reason,
        "message":    message
    }


@router.get("/checkin/history")
def checkin_history(user: dict = Depends(require_role("patient"))):
    """Returns last 10 check-ins for this patient."""
    result = supabase.table("checkins")\
        .select("*")\
        .eq("patient_id", user["id"])\
        .order("checked_in_at", desc=True)\
        .limit(10)\
        .execute()

    demo_log("History", {"patient": user["full_name"],
                         "records": len(result.data)})
    return result.data


# ── Internal alert helper ─────────────────────────────────────────

def _fire_alert(user: dict, risk_level: str,
                reason: str, condition: str):
    """Saves alert to DB and sends SMS to caregiver."""

    # Find caregiver
    link = supabase.table("caregiver_patients")\
        .select("caregiver_id")\
        .eq("patient_id", user["id"])\
        .execute()

    caregiver_id    = None
    caregiver_phone = None

    if link.data:
        caregiver_id = link.data[0]["caregiver_id"]
        cg = supabase.table("users")\
            .select("phone, full_name")\
            .eq("id", caregiver_id)\
            .execute()
        if cg.data:
            caregiver_phone = cg.data[0]["phone"]

    # Save alert
    supabase.table("alerts").insert({
        "patient_id":   user["id"],
        "caregiver_id": caregiver_id,
        "risk_level":   risk_level,
        "reason":       reason,
        "condition":    condition,
        "is_resolved":  False,
    }).execute()

    # Send SMS
    if caregiver_phone or DEMO_MODE:
        phone = caregiver_phone or "+256700000002"
        send_sms(phone, (
            f"CARECOMPANION ALERT\n"
            f"Patient: {user['full_name']}\n"
            f"Condition: {condition.upper()}\n"
            f"Risk level: {risk_level}\n"
            f"Reason: {reason}\n"
            f"Please check on them now."
        ))