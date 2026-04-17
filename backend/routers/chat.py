from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.auth import require_role
from database import supabase
from services.notifier import send_sms
from utils.demo import DEMO_MODE, demo_log
import os

router = APIRouter()

# ── Condition-specific system prompts ─────────────────────────────
# Claude receives a different persona per condition.
# Each prompt keeps the same warm tone but focuses on
# clinically relevant guidance for that condition.

CONDITION_PROMPTS = {
    "diabetes": """
You are a caring health companion supporting a patient managing diabetes 
in Uganda. You speak simply, warmly, and clearly.
Your focus areas: blood sugar monitoring, insulin or metformin adherence, 
diet (avoiding sugar and white carbs), hydration, and recognising 
danger signs (confusion, extreme thirst, blurred vision).
Never diagnose. Always encourage clinic visits for serious symptoms.
Keep responses to 2-4 sentences maximum.
""",
    "gestational_diabetes": """
You are a caring health companion supporting a pregnant woman managing 
gestational diabetes in Uganda. Speak gently and reassuringly.
Your focus areas: blood sugar monitoring, fetal movement, diet, 
medication adherence, and antenatal appointments.
Danger signs to escalate immediately: no fetal movement, severe headache, 
sudden swelling, blurred vision. Tell her to go to the clinic immediately.
Keep responses to 2-4 sentences maximum.
""",
    "hiv": """
You are a caring health companion supporting a patient living with HIV 
in Uganda who is on ART treatment. Speak with dignity, warmth, and 
without stigma.
Your focus areas: daily ART adherence (same time every day), 
managing side effects, nutrition, clinic follow-ups, and viral load tests.
Danger signs: missed doses streak, fever, severe fatigue, weight loss.
Never reveal the patient's status in any message visible to others.
Keep responses to 2-4 sentences maximum.
""",
    "hypertension": """
You are a caring health companion supporting a patient managing 
hypertension (high blood pressure) in Uganda. Speak calmly and clearly.
Your focus areas: daily medication adherence, blood pressure monitoring, 
low-salt diet, avoiding stress, hydration, and clinic follow-ups.
Danger signs to escalate: severe headache, chest pain, nosebleed, 
sudden blurred vision — advise immediate clinic visit.
Keep responses to 2-4 sentences maximum.
""",
    "eclampsia": """
You are a caring health companion supporting a high-risk pregnant woman 
with eclampsia in Uganda. Speak with urgency when needed but always 
with warmth and calm.
Your focus areas: blood pressure monitoring, swelling, fetal movement, 
medication adherence, and immediate escalation of danger signs.
Danger signs requiring IMMEDIATE action: severe headache, blurred vision, 
sudden swelling, no fetal movement, seizure signs.
For any danger sign: tell her clearly to go to the hospital NOW 
and that her caregiver has been notified.
Keep responses to 2-4 sentences maximum.
""",
    "cancer_remission": """
You are a caring health companion supporting a cancer patient in 
remission in Uganda. Speak with hope, encouragement, and warmth.
Your focus areas: medication adherence, energy levels, attending 
follow-up oncology appointments, nutrition, and reporting new symptoms.
New symptoms to escalate immediately: new lump, unexplained bleeding, 
severe unexplained weight loss, persistent new pain.
Keep responses to 2-4 sentences maximum.
""",
}

# ── Demo replies — keyword matched per condition ───────────────────

DEMO_REPLIES = {
    "diabetes": {
        "thirst":      "Extreme thirst can be a sign your blood sugar is high. Please take your medication and drink clean water. Check your blood sugar if you can.",
        "sugar":       "Try to avoid sweet foods and white bread today. Take your medication and drink water. If you feel confused or very weak, go to the clinic immediately.",
        "medication":  "Take your medication at the same time every day — it keeps your blood sugar stable. Would you like me to set a reminder?",
        "weak":        "Weakness can mean your blood sugar is low or high. Take your medication and eat a small meal. If it gets worse, please go to the clinic.",
        "default":     "Thank you for checking in. How is your blood sugar today? Have you taken your medication?",
    },
    "gestational_diabetes": {
        "movement":    "Baby movement is very important. If you feel less movement than usual, please go to the clinic today — do not wait.",
        "sugar":       "Keep monitoring your blood sugar morning and evening. Avoid sweet drinks and white rice. Your baby depends on your sugar being stable.",
        "headache":    "A severe headache during pregnancy needs attention immediately. Please go to your antenatal clinic now.",
        "swelling":    "Sudden swelling in your face or hands is a warning sign. Please go to the clinic today.",
        "default":     "How are you and baby doing today? Have you checked your blood sugar this morning?",
    },
    "hiv": {
        "medication":  "Taking your ART every day at the same time is the most important thing you can do. Even one missed dose matters. You are protecting yourself.",
        "tired":       "Fatigue can be a side effect of ART or a sign your body needs support. Rest well, eat nutritious food, and let your clinic know if it persists.",
        "fever":       "A fever while on ART needs medical attention. Please go to your clinic today — do not wait.",
        "side":        "Side effects can be difficult. Please tell your clinic — they may be able to adjust your medication. Do not stop taking ART on your own.",
        "default":     "Well done for checking in. Have you taken your ART today? Remember — same time every day.",
    },
    "hypertension": {
        "headache":    "A severe headache with high blood pressure needs attention. Take your medication now and rest. If it does not improve in 30 minutes, go to the clinic.",
        "pressure":    "Keep taking your medication every day even if you feel fine — high blood pressure often has no symptoms. Reduce salt in your food.",
        "chest":       "Chest pain with high blood pressure is a serious warning sign. Please go to the clinic or hospital immediately.",
        "medication":  "Your blood pressure medication works best when taken every day. Never stop without talking to your doctor first.",
        "default":     "How are you feeling today? Have you taken your blood pressure medication?",
    },
    "eclampsia": {
    "headache":    "A severe headache during pregnancy with high blood pressure is a serious warning sign. Please go to the hospital now. Your caregiver has been notified.",
    "vision":      "Blurred vision during pregnancy needs urgent attention. Please go to the hospital immediately — do not wait.",
    "swelling":    "Sudden swelling in your face or hands is dangerous with eclampsia. Please go to the hospital now.",
    "moving":      "If your baby is moving less than usual, go to the clinic immediately. Do not wait to see if it improves.",
    "movement":    "If your baby is moving less than usual, go to the clinic immediately. Do not wait to see if it improves.",
    "baby":        "Baby movement is very important. If baby is moving less than usual, go to the clinic immediately.",
    "scared":      "It is okay to feel scared. You are not alone — your caregiver and your clinic know your situation. Please go to the hospital now for your safety and your baby's safety.",
    "weak":        "Weakness during pregnancy needs attention. Please rest, drink water, and take your medication. If it gets worse, go to the clinic today.",
    "tired":       "Fatigue is common but please rest and stay hydrated. If you feel very weak or dizzy, contact your clinic today.",
    "pain":        "Pain during pregnancy should not be ignored. Please contact your midwife or go to the clinic today.",
    "nausea":      "Nausea during pregnancy is common but please stay hydrated and eat small meals. If it is severe or you cannot keep food down, contact your midwife.",
    "nauseous":    "Nausea during pregnancy is common but please stay hydrated and eat small meals. If it is severe or you cannot keep food down, contact your midwife.",
    "medication":  "Please take your medication as soon as you remember. Missing doses with eclampsia is serious — contact your midwife if you are unsure what to do.",
    "missed":      "Missing your medication with eclampsia needs attention. Please take it now if it has not been too long, and contact your midwife today.",
    "default":     "How are you feeling today, and how is baby moving? Please tell me your symptoms.",
},
    "cancer_remission": {
        "tired":       "Fatigue after cancer treatment is common. Rest when you need to, eat well, and stay hydrated. Tell your oncologist if the fatigue is severe.",
        "lump":        "A new lump needs to be checked by your doctor immediately. Please contact your oncology clinic today.",
        "pain":        "Persistent new pain should be reported to your clinic. Please contact your oncologist — do not ignore new symptoms.",
        "appointment": "Your follow-up appointments are very important for staying well. Please do not skip them — early detection protects you.",
        "default":     "How are you feeling today? Any new symptoms to report? Remember your next follow-up appointment is coming soon.",
    },
}


def _get_demo_reply(condition: str, message: str) -> str:
    """Keyword-matches a realistic reply for demo mode."""
    replies = DEMO_REPLIES.get(condition, DEMO_REPLIES["diabetes"])
    msg     = message.lower()

    # Score each keyword by how well it matches
    best_match  = None
    best_length = 0

    for keyword, reply in replies.items():
        if keyword != "default" and keyword in msg:
            # Prefer longer keyword matches — more specific wins
            if len(keyword) > best_length:
                best_match  = reply
                best_length = len(keyword)

    return best_match if best_match else replies["default"]


# ── Request model ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


# ── Endpoints ─────────────────────────────────────────────────────

@router.post("/chat")
def chat(
    data: ChatRequest,
    user: dict = Depends(require_role("patient"))
):
    condition = user.get("condition", "diabetes")

    if DEMO_MODE:
        reply = _get_demo_reply(condition, data.message)
        demo_log("Chat", {
            "patient":   user["full_name"],
            "condition": condition,
            "message":   data.message,
            "reply":     reply
        })
        # Still save to DB (fake in demo mode)
        supabase.table("messages").insert([
            {"patient_id": user["id"],
             "role": "user", "content": data.message},
            {"patient_id": user["id"],
             "role": "assistant", "content": reply},
        ]).execute()
        return {"reply": reply, "mode": "demo"}

    # ── Live mode — real Claude API call ──────────────────────────
    try:
        import anthropic
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Load last 10 messages for conversation context
        history = supabase.table("messages")\
            .select("role, content")\
            .eq("patient_id", user["id"])\
            .order("created_at", desc=False)\
            .limit(10)\
            .execute()

        conversation = [
            {"role": m["role"], "content": m["content"]}
            for m in history.data
        ]
        conversation.append({
            "role": "user",
            "content": data.message
        })

        system_prompt = CONDITION_PROMPTS.get(
            condition,
            CONDITION_PROMPTS["diabetes"]
        )

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            system=system_prompt,
            messages=conversation
        )
        reply = response.content[0].text

        # Save both turns to DB
        supabase.table("messages").insert([
            {"patient_id": user["id"],
             "role": "user",      "content": data.message},
            {"patient_id": user["id"],
             "role": "assistant", "content": reply},
        ]).execute()

        return {"reply": reply, "mode": "live"}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Chat error: {str(e)}")


@router.get("/chat/history")
def chat_history(user: dict = Depends(require_role("patient"))):
    """Returns last 20 messages for this patient."""
    result = supabase.table("messages")\
        .select("role, content, created_at")\
        .eq("patient_id", user["id"])\
        .order("created_at", desc=False)\
        .limit(20)\
        .execute()

    demo_log("Chat history", {
        "patient": user["full_name"],
        "messages": len(result.data)
    })
    return result.data