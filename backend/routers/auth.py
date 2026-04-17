import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from database import supabase
from utils.demo import DEMO_MODE, demo_log

router = APIRouter()
security = HTTPBearer()

# ── Request / Response models ──────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    role: str        # 'patient', 'caregiver', 'admin'
    condition: str | None = None   # required if role == patient

# ── Demo user store (only used when DEMO_MODE=true) ────────────────

DEMO_USERS = {
    "patient@demo.com": {
        "id":         "demo-patient-001",
        "full_name":  "Nakato Sarah",
        "role":       "patient",
        "condition":  "eclampsia",
        "phone":      "+256700000001",
        "token":      "demo-token-patient"
    },
    "caregiver@demo.com": {
        "id":         "demo-caregiver-001",
        "full_name":  "Mukasa John",
        "role":       "caregiver",
        "condition":  None,
        "phone":      "+256700000002",
        "token":      "demo-token-caregiver"
    },
    "admin@demo.com": {
        "id":         "demo-admin-001",
        "full_name":  "Dr. Apio Grace",
        "role":       "admin",
        "condition":  None,
        "phone":      "+256700000003",
        "token":      "demo-token-admin"
    },
    "diabetes@demo.com": {
        "id":         "demo-patient-002",
        "full_name":  "Okello James",
        "role":       "patient",
        "condition":  "diabetes",
        "phone":      "+256700000004",
        "token":      "demo-token-diabetes"
    },
    "hiv@demo.com": {
        "id":         "demo-patient-003",
        "full_name":  "Nambi Grace",
        "role":       "patient",
        "condition":  "hiv",
        "phone":      "+256700000005",
        "token":      "demo-token-hiv"
    },
}

# ── Auth helpers ───────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validates the bearer token and returns the current user.
    In DEMO_MODE: matches token against DEMO_USERS.
    In LIVE mode: validates against Supabase Auth.
    """
    token = credentials.credentials

    if DEMO_MODE:
        for user in DEMO_USERS.values():
            if user["token"] == token:
                demo_log("Auth", {"user": user["full_name"],
                                  "role": user["role"]})
                return user
        raise HTTPException(status_code=401,
                            detail="Invalid demo token")

    # Live mode — verify with Supabase
    try:
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401,
                                detail="Invalid or expired token")

        # Fetch full profile from users table
        profile = supabase.table("users")\
            .select("*")\
            .eq("id", response.user.id)\
            .single()\
            .execute()

        if not profile.data:
            raise HTTPException(status_code=404,
                                detail="User profile not found")
        return profile.data

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_role(*roles: str):
    """
    Dependency factory — restricts an endpoint to specific roles.
    Usage: Depends(require_role('admin')) or
           Depends(require_role('patient', 'caregiver'))
    """
    def _check(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {', '.join(roles)}"
            )
        return user
    return _check

# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/auth/login")
def login(data: LoginRequest):
    if DEMO_MODE:
        user = DEMO_USERS.get(data.email)
        if not user:
            raise HTTPException(status_code=401,
                                detail="Unknown demo user")
        demo_log("Login", {"email": data.email,
                           "role": user["role"]})
        return {
            "token":      user["token"],
            "user_id":    user["id"],
            "full_name":  user["full_name"],
            "role":       user["role"],
            "condition":  user["condition"],
            "redirect_to": _get_redirect(user["role"],
                                         user["condition"])
        }

    # Live mode
    try:
        response = supabase.auth.sign_in_with_password({
            "email":    data.email,
            "password": data.password
        })
        profile = supabase.table("users")\
            .select("*")\
            .eq("id", response.user.id)\
            .single()\
            .execute()

        user = profile.data
        return {
            "token":      response.session.access_token,
            "user_id":    user["id"],
            "full_name":  user["full_name"],
            "role":       user["role"],
            "condition":  user.get("condition"),
            "redirect_to": _get_redirect(user["role"],
                                         user.get("condition"))
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/register")
def register(data: RegisterRequest):
    if data.role == "patient" and not data.condition:
        raise HTTPException(
            status_code=400,
            detail="condition is required for patient registration"
        )

    if DEMO_MODE:
        demo_log("Register", {"email": data.email,
                              "role": data.role,
                              "condition": data.condition})
        return {"message": "Demo mode — registration simulated",
                "role": data.role,
                "condition": data.condition}

    # Live mode
    try:
        auth_response = supabase.auth.sign_up({
            "email":    data.email,
            "password": data.password
        })
        supabase.table("users").insert({
            "id":        auth_response.user.id,
            "full_name": data.full_name,
            "phone":     data.phone,
            "role":      data.role,
            "condition": data.condition
        }).execute()

        return {"message": "Registration successful",
                "user_id": auth_response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    """Returns current user profile + redirect destination."""
    return {
        "user_id":    user["id"],
        "full_name":  user["full_name"],
        "role":       user["role"],
        "condition":  user.get("condition"),
        "redirect_to": _get_redirect(user["role"],
                                     user.get("condition"))
    }


def _get_redirect(role: str, condition: str | None) -> str:
    """
    Returns the frontend route this user should land on after login.
    Frontend reads this and navigates accordingly.
    """
    if role == "admin":
        return "/facility"
    if role == "caregiver":
        return "/caregiver"
    # Patient — route to their condition dashboard
    routes = {
        "diabetes":            "/dashboard/diabetes",
        "gestational_diabetes": "/dashboard/gestational",
        "hiv":                 "/dashboard/hiv",
        "hypertension":        "/dashboard/hypertension",
        "eclampsia":           "/dashboard/eclampsia",
        "cancer_remission":    "/dashboard/cancer",
    }
    return routes.get(condition, "/dashboard")