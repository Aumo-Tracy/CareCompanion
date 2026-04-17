import os
from utils.demo import DEMO_MODE, demo_log
from services.notifier import send_sms

# ── Demo patient states (simulates reading from Supabase) ──────────

DEMO_PATIENT_STATES = [
    {
        "id":          "demo-patient-001",
        "name":        "Sarah",
        "phone":       "+256700000001",
        "condition":   "eclampsia",
        "risk_level":  "HIGH",
        "missed_doses": 2,
        "last_symptoms": ["severe_headache", "swelling"],
        "medication":  "Methyldopa 250mg",
    },
    {
        "id":          "demo-patient-002",
        "name":        "James",
        "phone":       "+256700000004",
        "condition":   "diabetes",
        "risk_level":  "HIGH",
        "missed_doses": 3,
        "last_symptoms": ["blurred_vision"],
        "medication":  "Metformin 500mg",
    },
    {
        "id":          "demo-patient-003",
        "name":        "Grace",
        "phone":       "+256700000005",
        "condition":   "hiv",
        "risk_level":  "MEDIUM",
        "missed_doses": 1,
        "last_symptoms": ["fatigue"],
        "medication":  "Dolutegravir/TDF/3TC",
    },
]

# ── Agent prompt builder ───────────────────────────────────────────

def _build_agent_prompt(patient: dict) -> str:
    symptoms = ", ".join(patient["last_symptoms"]) \
               if patient["last_symptoms"] else "none reported"
    return f"""
You are a health reminder agent for CareCompanion in Uganda.

Patient context:
- Name: {patient['name']}
- Condition: {patient['condition']}
- Current risk level: {patient['risk_level']}
- Missed doses: {patient['missed_doses']}
- Last reported symptoms: {symptoms}
- Medication due: {patient['medication']}

Write a short SMS reminder (maximum 3 sentences) that:
1. Addresses their specific situation — not a generic reminder
2. Mentions their risk level if HIGH or MEDIUM
3. Is warm, simple, and encouraging
4. Ends with: Reply 1 if taken, 2 if not yet

Write only the SMS text. No subject line, no explanation.
"""

# ── Agent decision logic ───────────────────────────────────────────

def _should_send(patient: dict) -> bool:
    """
    Agent decides whether to send a reminder at all.
    No point reminding a LOW risk patient who already took all meds.
    """
    if patient["risk_level"] == "LOW" and patient["missed_doses"] == 0:
        return False
    return True

# ── Demo fallback messages (no API cost) ──────────────────────────

DEMO_AGENT_MESSAGES = {
    "HIGH": (
        "Hi {name}, your health needs urgent attention today. "
        "Please take your {medication} now — you have missed "
        "{missed} dose(s) and your risk is HIGH. "
        "Reply 1 if taken, 2 if not yet."
    ),
    "MEDIUM": (
        "Hi {name}, please remember to take your {medication} today. "
        "You missed {missed} dose(s) recently — staying consistent "
        "helps keep you well. "
        "Reply 1 if taken, 2 if not yet."
    ),
    "LOW": (
        "Hi {name}, time to take your {medication}. "
        "You are doing well — keep it up! "
        "Reply 1 if taken, 2 if not yet."
    ),
}

def _demo_message(patient: dict) -> str:
    template = DEMO_AGENT_MESSAGES.get(
        patient["risk_level"],
        DEMO_AGENT_MESSAGES["LOW"]
    )
    return template.format(
        name=patient["name"],
        medication=patient["medication"],
        missed=patient["missed_doses"],
    )

# ── Main agent function ────────────────────────────────────────────

def run_reminder_agent(from_supabase: list = None):
    """
    The AI agent loop:
    1. Observe — get all patients due for reminders
    2. Reason — decide what each patient needs to hear
    3. Act — send personalised SMS

    In DEMO_MODE: uses hardcoded patient states, no API calls.
    In LIVE mode: reads from Supabase, calls Claude for each message.
    """
    patients = from_supabase or DEMO_PATIENT_STATES

    demo_log("Agent started", {
        "patients": len(patients),
        "mode": "demo" if DEMO_MODE else "live"
    })

    results = []

    for patient in patients:

        # Observe + Reason: should this patient get a reminder?
        if not _should_send(patient):
            demo_log("Agent skip", {
                "patient": patient["name"],
                "reason": "LOW risk, no missed doses"
            })
            continue

        if DEMO_MODE:
            # Demo mode: intelligent template, no API cost
            message = _demo_message(patient)
            demo_log("Agent message (demo)", {
                "patient":   patient["name"],
                "risk":      patient["risk_level"],
                "missed":    patient["missed_doses"],
                "message":   message
            })
        else:
            # Live mode: Claude reasons about this specific patient
            try:
                import anthropic
                client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=150,
                    messages=[{
                        "role": "user",
                        "content": _build_agent_prompt(patient)
                    }]
                )
                message = response.content[0].text.strip()
            except Exception as e:
                print(f"[Agent error] {patient['name']}: {e}")
                message = _demo_message(patient)

        # Act: send the SMS
        send_sms(patient["phone"], message)
        results.append({
            "patient":  patient["name"],
            "risk":     patient["risk_level"],
            "sent":     True,
            "message":  message
        })

    demo_log("Agent complete", {
        "sent": len(results),
        "skipped": len(patients) - len(results)
    })

    return results