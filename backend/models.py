from pydantic import BaseModel
from typing import List, Optional

class CheckInRequest(BaseModel):
    patient_id: str
    meds_taken: str            # 'all', 'some', 'none'
    symptoms: List[str]        # e.g. ['weakness', 'dizziness']
    mood: int                  # 1 to 5

class CheckInResponse(BaseModel):
    risk_level: str            # 'low', 'medium', 'high'
    risk_score: int
    message: str               # encouraging message back to patient

class ChatRequest(BaseModel):
    patient_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

class AlertResponse(BaseModel):
    id: str
    patient_id: str
    risk_level: str
    reason: str
    is_resolved: bool