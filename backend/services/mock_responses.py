import random

# ── Claude companion ───────────────────────────────────────────────
CHAT_RESPONSES = [
    "I hear you. Make sure you've had water today and try to rest. "
    "Your body is working hard and needs support.",

    "Thank you for telling me how you feel. Please take your medications "
    "if you haven't yet. I'm keeping an eye on you.",

    "That sounds uncomfortable. If things get worse, please tell your "
    "caregiver or visit your nearest clinic.",

    "You're doing well by checking in. Keep going — small steps matter.",

    "I'm sorry you're feeling this way. Rest, hydrate, and take your "
    "medication. You are not alone in this.",
]

def mock_chat_reply(message: str) -> str:
    """Returns a realistic-sounding companion reply without hitting Claude."""
    msg = message.lower()
    if any(w in msg for w in ["weak", "tired", "pain", "hurt"]):
        return (
            "I'm sorry you're feeling that way. Please rest and make sure "
            "you've taken your medications. If it gets worse, let your "
            "caregiver know right away."
        )
    if any(w in msg for w in ["good", "fine", "okay", "great"]):
        return (
            "That's wonderful to hear! Keep up with your medications and "
            "stay hydrated. You're doing great."
        )
    if any(w in msg for w in ["miss", "forgot", "skip"]):
        return (
            "It's okay — take your medication now if it's not too late in "
            "the day. Try to set a daily alarm so it becomes a habit."
        )
    return random.choice(CHAT_RESPONSES)


# ── SMS / Africa's Talking ─────────────────────────────────────────
def mock_send_sms(phone: str, message: str) -> dict:
    """Logs the SMS locally instead of sending it."""
    print(f"\n[MOCK SMS] To: {phone}\n{message}\n")
    return {"status": "mocked", "phone": phone}


# ── Risk scorer (already free — but useful for UI testing) ─────────
def mock_checkin_response(meds_taken: str, symptoms: list) -> dict:
    """Returns a hardcoded risk result for UI flow testing."""
    if meds_taken == "none" or len(symptoms) >= 3:
        return {"risk_level": "high",   "risk_score": 8,
                "message": "We're concerned. Your caregiver has been notified."}
    if meds_taken == "some" or len(symptoms) >= 1:
        return {"risk_level": "medium", "risk_score": 4,
                "message": "Please take your medications and rest well."}
    return    {"risk_level": "low",    "risk_score": 1,
                "message": "You're doing well today. Keep it up!"}