# CareCompanion — Master Handoff Document
Last updated: April 2026

---

## One-line pitch
AI-powered daily care companion for high-risk patients in Uganda,
centralised through health facilities, with condition-specific
dashboards and caregiver integration.

---

## Product context

### Users (4 roles)
- Health facility admin — registers patients, monitors all conditions,
  receives all alerts
- Patient — logs in, auto-routed to their condition dashboard
- Caregiver — receives alerts, does weekly support check-in
- (Future) Community health worker

### Conditions supported
| Condition | Key metric | Critical alert trigger |
|---|---|---|
| Diabetes | Blood sugar + insulin | Missed 2+ doses or sugar crisis |
| Gestational diabetes | Blood sugar + fetal movement | Any danger sign |
| HIV | ART adherence | Missed 3+ doses or opportunistic signs |
| Hypertension | BP reading + medication | BP flagged HIGH by scorer |
| Eclampsia | BP + swelling + fetal movement | Any flag → immediate |
| Cancer remission | Medication + new symptoms | New symptom reported |

### Demo day: June 30th
### Seniors demo: Lovable prototype built, 9 prompts completed

---

## Tech stack (fixed — never change)

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI + Python | Complete, tested, running |
| Database | Supabase | Project created, schema run |
| Auth | Supabase Auth | condition field drives all routing |
| Risk engine | Rule-based scorer | Explainable, never change philosophy |
| Scheduler | APScheduler | Running on startup, fires every hour |
| SMS | Africa's Talking | Mocked in demo mode |
| AI chat | Claude API | Mocked in demo mode, prompt per condition |
| Prototype | Lovable | Built — 9 prompts, 12 screens |
| Production frontend | SvelteKit | Next to build |

---

## Personalisation + auth routing logic

1. Patient logs in → Supabase Auth returns JWT
2. JWT sent with every FastAPI request as Bearer token
3. FastAPI reads condition from user record
4. condition field routes to correct dashboard, check-in
   questions, AI system prompt, and risk weights
5. No patient ever sees another condition's screen
6. Caregiver linked via caregiver_patients table
7. Facility admin has role = 'admin' — sees all patients

---

## Project structure