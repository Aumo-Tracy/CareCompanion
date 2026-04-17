from fastapi import APIRouter
from database import supabase

router = APIRouter()


@router.get("/alerts/{caregiver_id}")
async def get_alerts(caregiver_id: str):
    response = supabase.table("alerts")\
        .select("*, users!alerts_patient_id_fkey(full_name, condition)")\
        .eq("caregiver_id", caregiver_id)\
        .eq("is_resolved", False)\
        .order("created_at", desc=True)\
        .execute()
    return response.data


@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    supabase.table("alerts")\
        .update({"is_resolved": True})\
        .eq("id", alert_id)\
        .execute()
    return {"status": "resolved"}