from routers.auth import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.demo import DEMO_MODE, demo_log
from services.risk_scorer import calculate_risk
from services.notifier import send_sms
from routers.checkin import router as checkin_router
from routers.chat import router as chat_router
from routers.facility import router as facility_router
from routers.reminders import router as reminders_router
from routers.reminders import start_scheduler



load_dotenv()

app = FastAPI(title="CareCompanion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(checkin_router)
app.include_router(chat_router)
app.include_router(facility_router)
app.include_router(reminders_router)

@app.on_event("startup")          
def on_startup():                  
    start_scheduler()   

@app.get("/health")
def health():
    return {
        "status": "ok",
        "demo_mode": DEMO_MODE,
        "services": {
            "database":  "mocked" if DEMO_MODE else "supabase",
            "sms":       "mocked" if DEMO_MODE else "africa's talking",
            "ai":        "mocked" if DEMO_MODE else "claude api",
        }
    }


@app.post("/demo/simulate")
def simulate():
    """
    Full demo journey — no external calls needed.
    Patient checks in → risk scored → caregiver alerted.
    """
    patient_name  = "Nakato Sarah"
    patient_phone = "+256700000001"
    caregiver_phone = "+256700000002"
    condition     = "pregnancy"
    symptoms      = ["headache", "swelling"]
    missed_doses  = 2

    # Score the risk
    result = calculate_risk(symptoms, missed_doses)

    # Fire caregiver SMS if HIGH
    sms_sent = False
    if result["risk_level"] == "HIGH":
        message = (
            f"ALERT: {patient_name} needs attention.\n"
            f"Risk: {result['risk_level']}\n"
            f"Reason: {result['reason']}\n"
            f"Please check on them now."
        )
        send_sms(caregiver_phone, message)
        sms_sent = True

    demo_log("Simulation complete", {
        "patient":   patient_name,
        "risk":      result["risk_level"],
        "score":     result["score"],
        "sms_sent":  sms_sent
    })

    return {
        "patient":            patient_name,
        "condition":          condition,
        "symptoms_reported":  symptoms,
        "missed_doses":       missed_doses,
        "risk_score":         result["score"],
        "risk_level":         result["risk_level"],
        "reason":             result["reason"],
        "caregiver_alerted":  sms_sent
    }