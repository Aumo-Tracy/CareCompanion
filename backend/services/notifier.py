from utils.demo import DEMO_MODE, demo_log

def send_sms(phone: str, message: str) -> dict:
    if DEMO_MODE:
        demo_log("SMS", {"to": phone, "message": message})
        return {"status": "mocked", "to": phone}

    import africastalking
    import os
    africastalking.initialize(
        username=os.getenv("AT_USERNAME"),
        api_key=os.getenv("AT_API_KEY")
    )
    try:
        response = africastalking.SMS.send(message, [phone])
        return {"status": "sent", "response": response}
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return {"status": "failed", "error": str(e)}