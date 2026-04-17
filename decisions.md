# CareCompanion — Decisions Log
Append only. Never delete entries.

---

2026-04  Dropped mood from risk scorer
         Reason: keeps scoring clinically explainable.
         Mood collected in check-in UI, stored separately, 
         not factored into risk score.

2026-04  DEMO_MODE=true is the permanent default
         Reason: prevents accidental API credit burn.
         Only flip to false for targeted real API testing, 
         maximum 5-10 calls, then flip back.

2026-04  Rule-based scorer — no ML, no black box
         Reason: explainable to clinicians and demo judges.
         Every risk point traceable to a clinical reason.
         Do not introduce weighted ML models before June 30th.

2026-04  Lovable for seniors demo, SvelteKit for production
         Reason: Lovable is fast for a simulated demo this week.
         SvelteKit is flexible, interactivity-friendly, 
         and supports the monetisation path long term.

2026-04  SMS/WhatsApp is primary patient channel, not the app
         Reason: device access and data costs are real in Uganda.
         App is for caregivers and facility admins primarily.
         Patients interact mainly via SMS reply (1/2/3 choices).

2026-04  Cancer included — post-treatment remission only
         Reason: active chemo and palliative care are 
         different scopes. Remission fits the daily 
         monitoring model cleanly.

2026-04  Condition field on Supabase user record drives all routing
         Reason: one login, one token, condition determines 
         dashboard, check-in questions, AI prompt, risk weights.
         No patient ever sees another condition's screen.

2026-04  Facility admin is central to the pitch
         Reason: centralised health facility tracking is 
         the business model. Facility pays, patients benefit.
         Admin view must be in every demo.

2026-04  Palliative care excluded
         Reason: completely different scope — pain management, 
         end of life,
          family support. Separate product entirely.

2026-04  Auth router registered without prefix in main.py
         Reason: routers/auth.py already defines /auth/* paths
         internally. Adding prefix="/api" caused /auth/auth/
         doubling. Rule: only add prefix in include_router when
         the router itself has no path prefix on its routes.

2026-04  /checkin requires Bearer token — 401 on unauthenticated calls
         This is correct behaviour. Frontend must always attach token
         from login response. Test in /docs using Authorize button
         before hitting protected endpoint

2026-04  Role-based access confirmed working
         admin → /facility/* endpoints only
         caregiver → /alerts/caregiver and /caregiver/patient only
         patient → /checkin and /chat only
         403 on wrong role is correct behaviour, not a bug.