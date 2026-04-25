import os

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

def demo_log(label: str, payload: dict):
    if DEMO_MODE:
        import json
        print(f"\n[DEMO] {label}:")
        print(json.dumps(payload, indent=2))