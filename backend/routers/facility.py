from fastapi import APIRouter, Depends, HTTPException
from routers.auth import require_role
from database import supabase
from utils.demo import DEMO_MODE, demo_log
from datetime import datetime

router = APIRouter()

# ── Demo data — shown when DEMO_MODE=true ─────────────────────────

DEMO_PATIENTS = [
    {
        "id":            "demo-patient-001",
        "full_name":     "Nakato Sarah",
        "age":           28,
        "condition":     "eclampsia",
        "risk_level":    "HIGH",
        "risk_score":    100,
        "last_checkin":  "Today 9:15am",
        "phone":         "+256700000001",
        "caregiver":     "Mukasa John",
    },
    {
        "id":            "demo-patient-002",
        "full_name":     "Okello James",
        "age":           45,
        "condition":     "diabetes",
        "risk_level":    "HIGH",
        "risk_score":    85,
        "last_checkin":  "Today 8:40am",
        "phone":         "+256700000004",
        "caregiver":     "Okello Rose",
    },
    {
        "id":            "demo-patient-003",
        "full_name":     "Nambi Grace",
        "age":           32,
        "condition":     "hiv",
        "risk_level":    "MEDIUM",
        "risk_score":    55,
        "last_checkin":  "Today 10:00am",
        "phone":         "+256700000005",
        "caregiver":     "Nambi Peter",
    },
    {
        "id":            "demo-patient-004",
        "full_name":     "Kato Richard",
        "age":           52,
        "condition":     "hypertension",
        "risk_level":    "MEDIUM",
        "risk_score":    45,
        "last_checkin":  "Yesterday",
        "phone":         "+256700000006",
        "caregiver":     "Kato Agnes",
    },
    {
        "id":            "demo-patient-005",
        "full_name":     "Achola Mary",
        "age":           24,
        "condition":     "gestational_diabetes",
        "risk_level":    "LOW",
        "risk_score":    15,
        "last_checkin":  "Today 11:00am",
        "phone":         "+256700000007",
        "caregiver":     "Achola David",
    },
    {
        "id":            "demo-patient-006",
        "full_name":     "Ssebunya Tom",
        "age":           38,
        "condition":     "cancer_remission",
        "risk_level":    "LOW",
        "risk_score":    10,
        "last_checkin":  "Today 7:30am",
        "phone":         "+256700000008",
        "caregiver":     "Ssebunya Faith",
    },
]

DEMO_ALERTS = [
    {
        "id":          "alert-001",
        "patient_id":  "demo-patient-001",
        "patient_name": "Nakato Sarah",
        "condition":   "eclampsia",
        "risk_level":  "HIGH",
        "reason":      "Symptoms: severe_headache, swelling | Missed 2 dose(s)",
        "caregiver":   "Mukasa John",
        "is_resolved": False,
        "created_at":  "Today 9:20am",
    },
    {
        "id":          "alert-002",
        "patient_id":  "demo-patient-002",
        "patient_name": "Okello James",
        "condition":   "diabetes",
        "risk_level":  "HIGH",
        "reason":      "Symptoms: blurred_vision, confusion | Missed 3 dose(s)",
        "caregiver":   "Okello Rose",
        "is_resolved": False,
        "created_at":  "Today 8:45am",
    },
    {
        "id":          "alert-003",
        "patient_id":  "demo-patient-003",
        "patient_name": "Nambi Grace",
        "condition":   "hiv",
        "risk_level":  "MEDIUM",
        "reason":      "Symptoms: severe_fatigue | Missed 2 dose(s)",
        "caregiver":   "Nambi Peter",
        "is_resolved": False,
        "created_at":  "Today 10:05am",
    },
]

DEMO_CAREGIVER_ALERTS = [
    {
        "id":          "alert-001",
        "patient_name": "Nakato Sarah",
        "condition":   "eclampsia",
        "risk_level":  "HIGH",
        "reason":      "Symptoms: severe_headache, swelling | Missed 2 dose(s)",
        "is_resolved": False,
        "created_at":  "Today 9:20am",
    },
    {
        "id":          "alert-old-001",
        "patient_name": "Nakato Sarah",
        "condition":   "eclampsia",
        "risk_level":  "MEDIUM",
        "reason":      "Missed evening medication",
        "is_resolved": True,
        "created_at":  "Yesterday 8:00pm",
    },
]


# ── Facility endpoints ────────────────────────────────────────────

@router.get("/facility/stats")
def facility_stats(user: dict = Depends(require_role("admin"))):
    """
    Summary numbers for the facility dashboard header.
    Admin sees this instantly on login.
    """
    if DEMO_MODE:
        high   = sum(1 for p in DEMO_PATIENTS if p["risk_level"] == "HIGH")
        medium = sum(1 for p in DEMO_PATIENTS if p["risk_level"] == "MEDIUM")
        low    = sum(1 for p in DEMO_PATIENTS if p["risk_level"] == "LOW")

        demo_log("Facility stats", {
            "admin":   user["full_name"],
            "total":   len(DEMO_PATIENTS),
            "high":    high,
        })
        return {
            "facility":        "Mulago National Referral Hospital",
            "total_patients":  len(DEMO_PATIENTS),
            "high_risk":       high,
            "medium_risk":     medium,
            "low_risk":        low,
            "checkins_today":  5,
            "alerts_today":    len(DEMO_ALERTS),
            "as_of":           datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # Live mode
    patients  = supabase.table("users")\
        .select("id")\
        .eq("role", "patient")\
        .execute()

    checkins  = supabase.table("checkins")\
        .select("risk_level")\
        .execute()

    alerts    = supabase.table("alerts")\
        .select("id")\
        .eq("is_resolved", False)\
        .execute()

    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in checkins.data:
        level = c.get("risk_level", "LOW")
        risk_counts[level] = risk_counts.get(level, 0) + 1

    return {
        "total_patients": len(patients.data),
        "high_risk":      risk_counts["HIGH"],
        "medium_risk":    risk_counts["MEDIUM"],
        "low_risk":       risk_counts["LOW"],
        "alerts_today":   len(alerts.data),
        "as_of":          datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@router.get("/facility/patients")
def facility_patients(user: dict = Depends(require_role("admin"))):
    """
    All patients sorted by risk level — HIGH first.
    """
    if DEMO_MODE:
        order  = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_patients = sorted(
            DEMO_PATIENTS,
            key=lambda p: order.get(p["risk_level"], 3)
        )
        demo_log("Facility patients", {
            "admin": user["full_name"],
            "count": len(sorted_patients)
        })
        return sorted_patients

    result = supabase.table("users")\
        .select("*")\
        .eq("role", "patient")\
        .execute()
    return result.data


@router.get("/facility/alerts")
def facility_alerts(user: dict = Depends(require_role("admin"))):
    """
    All unresolved alerts across the facility.
    """
    if DEMO_MODE:
        unresolved = [a for a in DEMO_ALERTS if not a["is_resolved"]]
        demo_log("Facility alerts", {
            "admin":    user["full_name"],
            "count":    len(unresolved)
        })
        return unresolved

    result = supabase.table("alerts")\
        .select("*, users!alerts_patient_id_fkey(full_name, condition)")\
        .eq("is_resolved", False)\
        .order("created_at", desc=True)\
        .execute()
    return result.data


# ── Caregiver endpoints ───────────────────────────────────────────

@router.get("/alerts/caregiver")
def caregiver_alerts(user: dict = Depends(require_role("caregiver"))):
    """
    Alerts for this caregiver's patients.
    """
    if DEMO_MODE:
        demo_log("Caregiver alerts", {
            "caregiver": user["full_name"],
            "count":     len(DEMO_CAREGIVER_ALERTS)
        })
        return DEMO_CAREGIVER_ALERTS

    result = supabase.table("alerts")\
        .select("*")\
        .eq("caregiver_id", user["id"])\
        .order("created_at", desc=True)\
        .limit(20)\
        .execute()
    return result.data


@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    user: dict = Depends(require_role("caregiver", "admin"))
):
    """
    Caregiver or admin marks an alert as handled.
    """
    if DEMO_MODE:
        demo_log("Alert resolved", {
            "alert_id": alert_id,
            "by":       user["full_name"]
        })
        return {
            "status":    "resolved",
            "alert_id":  alert_id,
            "resolved_by": user["full_name"]
        }

    supabase.table("alerts")\
        .update({"is_resolved": True})\
        .eq("id", alert_id)\
        .execute()
    return {"status": "resolved", "alert_id": alert_id}


@router.get("/caregiver/patient")
def caregiver_patient(user: dict = Depends(require_role("caregiver"))):
    """
    Returns the patient this caregiver is linked to.
    """
    if DEMO_MODE:
        demo_log("Caregiver patient lookup", {
            "caregiver": user["full_name"]
        })
        return {
            "patient_name": "Nakato Sarah",
            "condition":    "eclampsia",
            "risk_level":   "HIGH",
            "risk_score":   100,
            "last_checkin": "Today 9:15am",
            "phone":        "+256700000001",
            "alerts":       DEMO_CAREGIVER_ALERTS
        }

    link = supabase.table("caregiver_patients")\
        .select("patient_id")\
        .eq("caregiver_id", user["id"])\
        .execute()

    if not link.data:
        raise HTTPException(
            status_code=404,
            detail="No patient linked to this caregiver"
        )

    patient = supabase.table("users")\
        .select("*")\
        .eq("id", link.data[0]["patient_id"])\
        .single()\
        .execute()

    return patient.data