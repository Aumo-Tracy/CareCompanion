from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from routers.auth import require_role
from services.notifier import send_sms
from database import supabase
from utils.demo import DEMO_MODE, demo_log
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from services.reminder_agent import run_reminder_agent

router    = APIRouter()
scheduler = BackgroundScheduler()

# ── Demo medication schedules ─────────────────────────────────────

DEMO_MEDICATIONS = {
    "demo-patient-001": [
        {"id": "med-001", "name": "Methyldopa 250mg",
         "schedule_time": "08:00", "condition": "eclampsia"},
        {"id": "med-002", "name": "Labetalol 100mg",
         "schedule_time": "20:00", "condition": "eclampsia"},
    ],
    "demo-patient-002": [
        {"id": "med-003", "name": "Metformin 500mg",
         "schedule_time": "07:00", "condition": "diabetes"},
        {"id": "med-004", "name": "Metformin 500mg",
         "schedule_time": "19:00", "condition": "diabetes"},
    ],
    "demo-patient-003": [
        {"id": "med-005", "name": "Dolutegravir/TDF/3TC",
         "schedule_time": "21:00", "condition": "hiv"},
    ],
    "demo-patient-004": [
        {"id": "med-006", "name": "Amlodipine 5mg",
         "schedule_time": "08:00", "condition": "hypertension"},
    ],
    "demo-patient-005": [
        {"id": "med-007", "name": "Insulin (short-acting)",
         "schedule_time": "07:30", "condition": "gestational_diabetes"},
        {"id": "med-008", "name": "Folic acid 5mg",
         "schedule_time": "08:00", "condition": "gestational_diabetes"},
    ],
    "demo-patient-006": [
        {"id": "med-009", "name": "Tamoxifen 20mg",
         "schedule_time": "09:00", "condition": "cancer_remission"},
    ],
}

DEMO_PATIENTS_PHONES = {
    "demo-patient-001": ("+256700000001", "Sarah"),
    "demo-patient-002": ("+256700000004", "James"),
    "demo-patient-003": ("+256700000005", "Grace"),
    "demo-patient-004": ("+256700000006", "Richard"),
    "demo-patient-005": ("+256700000007", "Mary"),
    "demo-patient-006": ("+256700000008", "Tom"),
}

# ── Condition-specific reminder messages ──────────────────────────

REMINDER_MESSAGES = {
    "eclampsia":           "is very important for your blood pressure and your baby's safety.",
    "diabetes":            "helps keep your blood sugar stable throughout the day.",
    "hiv":                 "must be taken every day at the same time to keep your treatment working.",
    "hypertension":        "keeps your blood pressure under control. Never skip a dose.",
    "gestational_diabetes": "is important for you and your baby's health.",
    "cancer_remission":    "is part of your recovery. Keep taking it as prescribed.",
}


# ── Scheduler job — runs every hour ───────────────────────────────

def send_medication_reminders():
    """
    Checks all patient medication schedules every hour.
    Sends SMS reminder when schedule_time matches current hour.
    """
    current_time = datetime.now().strftime("%H:%M")
    current_hour = current_time[:3] + "00"

    if DEMO_MODE:
        demo_log("Scheduler tick", {"time": current_time})

        for patient_id, medications in DEMO_MEDICATIONS.items():
            phone, name = DEMO_PATIENTS_PHONES.get(
                patient_id, (None, "Patient")
            )
            for med in medications:
                if med["schedule_time"][:3] == current_hour[:3]:
                    condition_msg = REMINDER_MESSAGES.get(
                        med["condition"], "is due now."
                    )
                    message = (
                        f"Hi {name}, time to take your "
                        f"{med['name']}. This medication "
                        f"{condition_msg}\n"
                        f"Reply 1 if taken, 2 if not yet."
                    )
                    send_sms(phone or "+256700000001", message)
        return

    # Live mode — reads from Supabase
    try:
        meds = supabase.table("medications")\
            .select("*, users!medications_patient_id_fkey"
                    "(full_name, phone, condition)")\
            .eq("is_active", True)\
            .execute()

        for med in meds.data:
            scheduled = str(med.get("schedule_time", ""))[:5]
            if scheduled == current_time[:5]:
                patient   = med.get("users", {})
                phone     = patient.get("phone")
                name      = patient.get("full_name", "").split()[0]
                condition = patient.get("condition", "")

                if phone:
                    condition_msg = REMINDER_MESSAGES.get(
                        condition, "is due now."
                    )
                    send_sms(phone, (
                        f"Hi {name}, time to take your "
                        f"{med['name']}. This medication "
                        f"{condition_msg}\n"
                        f"Reply 1 if taken, 2 if not yet."
                    ))
    except Exception as e:
        print(f"[Scheduler error] {e}")


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            send_medication_reminders,
            "interval",
            hours=1,
            id="medication_reminders",
            replace_existing=True,
        )
        scheduler.start()
        print("[Scheduler] Medication reminder job started — runs every hour")


# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/reminders")
def get_reminders(user: dict = Depends(require_role("patient"))):
    """Returns upcoming medication reminders for this patient."""
    if DEMO_MODE:
        meds = DEMO_MEDICATIONS.get(user["id"], [])
        demo_log("Reminders", {
            "patient": user["full_name"],
            "count":   len(meds)
        })
        return {
            "patient":     user["full_name"],
            "medications": meds
        }

    result = supabase.table("medications")\
        .select("*")\
        .eq("patient_id", user["id"])\
        .eq("is_active", True)\
        .execute()
    return {
        "patient":     user["full_name"],
        "medications": result.data
    }


@router.post("/reminders/trigger")
def trigger_reminders_now(
    user: dict = Depends(require_role("admin"))
):
    """
    Admin manually fires the reminder job.
    Useful for demo — shows all mock SMS firing in terminal.
    """
    send_medication_reminders()
    demo_log("Manual reminder trigger", {"by": user["full_name"]})
    return {
        "status":  "triggered",
        "message": "Reminder job fired — check terminal for SMS logs"
    }
@router.post("/reminders/agent")
def run_agent(user: dict = Depends(require_role("admin"))):
    """
    Runs the AI reminder agent — observes patient states,
    reasons about each one, sends personalised SMS.
    This is the AI agent endpoint for the capstone demo.
    """
    results = run_reminder_agent()
    demo_log("Agent endpoint triggered", {
        "by":      user["full_name"],
        "results": len(results)
    })
    return {
        "status":   "completed",
        "agent":    "CareCompanion Reminder Agent",
        "sent":     len(results),
        "details":  results
    }