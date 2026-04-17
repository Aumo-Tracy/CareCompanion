# CareCompanion — AI-Powered High-Risk Patient Care Companion

## Problem
In Uganda, high-risk patients — pregnant mothers with eclampsia,
people living with HIV, diabetes and hypertension patients — frequently
fail between clinic visits. Medications are missed, symptoms are ignored,
caregivers are not kept in the loop, and risks are detected too late.
The gap between hospital visits is where most complications occur.

## Solution
CareCompanion is an AI-powered daily care companion that bridges this gap
through continuous monitoring, intelligent reminders, and early risk
detection — centralised through health facilities.

## How it works
A patient logs in and is automatically routed to their condition-specific
dashboard (6 conditions supported). They complete a daily check-in
reporting symptoms and medication adherence. A rule-based risk scorer
calculates their risk level and automatically alerts their caregiver via
SMS if HIGH risk is detected. An AI reminder agent observes each patient's
current state and uses Claude to compose personalised medication reminders
rather than generic messages. A Claude-powered companion chat responds to
patient messages with condition-aware clinical guidance. Health facility
admins monitor all patients across all conditions in real time.

## AI components
- Claude API (Anthropic) — conversational AI companion + agent reasoning
- Condition-specific prompt engineering — 6 clinical system prompts
- AI reminder agent — observe, reason, act pattern (Case 2: AI agents)
- Rule-based risk classification — explainable, clinician-friendly scoring

## Tech stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | Supabase (Postgres + Auth) |
| AI | Anthropic Claude API |
| Scheduler | APScheduler |
| SMS | Africa's Talking |
| Frontend | SvelteKit + Tailwind CSS |

## Running locally

### Backend
```bash
cd backend
pip install -r requirements.txt
# Set DEMO_MODE=true in .env for zero-cost development
uvicorn main:app --reload
# Docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

## Demo credentials
| Role | Email | Password |
|---|---|---|
| Patient (Eclampsia) | patient@demo.com | demo |
| Patient (Diabetes) | diabetes@demo.com | demo |
| Patient (HIV) | hiv@demo.com | demo |
| Caregiver | caregiver@demo.com | demo |
| Facility Admin | admin@demo.com | demo |

## Ethical considerations
- HIV patient privacy — condition never exposed in external messages
- Low literacy design — SMS replies use 1/2/3 number choices
- Explainable AI — every risk score traceable to clinical reasons
- DEMO_MODE architecture — prevents accidental real API calls during dev
- Caregiver alerts framed as "needs attention" not "emergency"

## Project status
- Backend: complete, all endpoints tested in demo mode
- Frontend: complete, all 12 screens across 4 user roles
- AI agent: complete, personalised reminders per patient state
- Demo day: June 30th
