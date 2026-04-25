# CareCompanion
### AI-Powered Daily Care Companion for High-Risk Patients in Uganda

---

## Project Summary

CareCompanion bridges the critical gap between clinic visits for high-risk 
patients in Uganda. Patients managing eclampsia, HIV, diabetes, hypertension, 
and gestational diabetes receive daily AI-powered monitoring, personalised 
medication reminders, and automatic caregiver alerts — all centralised through 
a health facility dashboard. Healthcare does not stop at the hospital door.

---

## Problem Statement

In Uganda, high-risk patients do not fail because treatment does not exist. 
They fail because there is no daily support system between hospital visits.

- Medications are missed with no follow-up
- Danger signs are ignored until it is too late  
- Caregivers are overwhelmed and uninformed
- Health facilities have no visibility between appointments

A pregnant mother with eclampsia may experience warning signs on Tuesday 
but only see her midwife on Friday. CareCompanion closes that gap.

---

## How It Works

1. Patient logs in → automatically routed to their condition-specific dashboard
2. Patient completes daily check-in — symptoms + medication adherence
3. Rule-based risk scorer calculates LOW / MEDIUM / HIGH risk
4. HIGH risk → caregiver receives automatic SMS alert instantly
5. AI reminder agent observes each patient's state → sends personalised SMS
6. AI companion chat responds with condition-aware clinical guidance
7. Facility admin monitors all patients across all conditions in real time

---

## AI Components

### 1. Claude API — AI Companion Chat
Each of the 6 supported conditions has its own clinical system prompt.
The AI understands whether it is speaking to a pregnant mother with 
eclampsia or an HIV patient on ART, and responds with condition-specific 
guidance in plain, simple language accessible to low-literacy users.

### 2. AI Reminder Agent (Observe → Reason → Act)
Rather than firing generic scheduled reminders, the agent:
- **Observes** each patient's current risk level, missed doses, and symptoms
- **Reasons** about what that specific patient needs to hear right now
- **Acts** by composing and sending a personalised SMS

Sarah with HIGH risk and 2 missed doses receives an urgent, specific message.
Grace with MEDIUM risk and 1 missed dose receives a gentler reminder.
LOW risk patients with no missed doses are skipped entirely.
This is Case 2 of the capstone — AI agent for task automation.

### 3. Prompt Engineering
Six condition-specific system prompts shape the AI's clinical persona,
tone, danger sign awareness, and escalation behaviour per condition.

### 4. Rule-Based Risk Classification
Intentionally explainable — every risk point is traceable to a clinical 
reason. Designed to be defensible to clinicians, not a black box.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI (Python) | Async, fast, Python ML-friendly |
| Database + Auth | Supabase | Postgres + real-time + auth in one |
| AI | Anthropic Claude API | Best-in-class conversational AI |
| Scheduler | APScheduler | Runs inside FastAPI, no extra service |
| SMS | Africa's Talking | Uganda-first, local East Africa integration |
| Frontend | SvelteKit | Fast, lightweight, mobile-first |

---

## Conditions Supported

| Condition | Key metric | Alert trigger |
|---|---|---|
| Eclampsia | BP + fetal movement | Any danger sign → immediate |
| Diabetes | Blood sugar + insulin | Missed 2+ doses or sugar crisis |
| Gestational diabetes | Blood sugar + fetal movement | Any danger sign |
| HIV | ART adherence | Missed 3+ doses or opportunistic signs |
| Hypertension | BP reading + medication | BP flagged HIGH |
| Cancer remission | Medication + new symptoms | New symptom reported |

---

## User Roles

- **Patient** — logs in, routed to condition dashboard, checks in daily
- **Caregiver** — receives alerts, does weekly support check-in
- **Facility Admin** — monitors all patients, triggers reminders, views stats

---

## DEMO_MODE Architecture

All external API calls are gated behind a single environment flag.

```bash
DEMO_MODE=true   # Zero cost — everything mocked locally
DEMO_MODE=false  # Real Supabase, Claude API, Africa's Talking SMS
```

This allows full development and testing with zero API costs.
Flipping one flag activates all real integrations with no code changes.

---

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # Add your keys
uvicorn main:app --reload
# API docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

---

## Demo Credentials

| Role | Email | Password |
|---|---|---|
| Patient — Eclampsia | patient@demo.com | demo |
| Patient — Diabetes | diabetes@demo.com | demo |
| Patient — HIV | hiv@demo.com | demo |
| Caregiver | caregiver@demo.com | demo |
| Facility Admin | admin@demo.com | demo |

---

## Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/login | Login, returns JWT + redirect route |
| POST | /checkin | Submit daily check-in, triggers risk scoring |
| POST | /chat | AI companion chat (Claude API) |
| GET | /facility/stats | Admin dashboard summary |
| GET | /alerts/caregiver | Caregiver alert feed |
| POST | /reminders/agent | Run AI reminder agent |
| POST | /demo/simulate | Full patient journey simulation |

---

## Ethical Considerations

- **HIV privacy** — condition never included in SMS or external messages
- **Low literacy design** — SMS uses Reply 1/2/3, no reading required
- **Explainable AI** — every risk score traceable to a clinical reason
- **Caregiver framing** — alerts say "needs attention" not "emergency"
- **Data minimisation** — only last 10 messages sent to Claude API
- **DEMO_MODE** — prevents accidental real patient data in dev/test

---

## Capstone Alignment

This project satisfies **Case 2: AI Agent for Task Automation** through 
the reminder agent's observe-reason-act pattern, and demonstrates:

- LLM API integration (Anthropic Claude)
- Prompt engineering (6 condition-specific system prompts)
- AI agent design (patient state observation + reasoning)
- Real-world impact (Uganda healthcare gap)
- Ethical AI considerations (privacy, literacy, explainability)

---

## Project Status

- Backend: complete, all 17 endpoints tested
- Frontend: complete, 12 screens across 4 user roles
- AI agent: confirmed working in demo and live mode
- Live database: Supabase connected, real check-ins working
