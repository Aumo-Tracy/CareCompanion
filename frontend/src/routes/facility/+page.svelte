<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let stats    = $state(null);
  let patients = $state([]);
  let alerts   = $state([]);
  let tab      = $state('patients');
  let loading  = $state(true);

  const conditionColors = {
    diabetes:            { bg: '#f0fdfa', color: '#0f766e', border: '#99f6e4' },
    gestational_diabetes:{ bg: '#f0fdfa', color: '#0f766e', border: '#99f6e4' },
    hiv:                 { bg: '#f5f3ff', color: '#7c3aed', border: '#ddd6fe' },
    hypertension:        { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
    eclampsia:           { bg: '#fff7ed', color: '#ea580c', border: '#fed7aa' },
    cancer_remission:    { bg: '#f9fafb', color: '#6b7280', border: '#e5e7eb' },
  };

  const riskColors = {
    HIGH:   { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
    MEDIUM: { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
    LOW:    { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' },
  };

  onMount(async () => {
    try {
      const [s, p, a] = await Promise.all([
        api.facilityStats(),
        api.facilityPatients(),
        api.facilityAlerts(),
      ]);
      stats    = s;
      patients = p;
      alerts   = a;
    } catch (e) {
      goto('/');
    } finally {
      loading = false;
    }
  });

  async function trigger() {
    await api.triggerReminders();
    alert('Reminders triggered — check backend terminal.');
  }

  function logout() { clearUser(); goto('/'); }
</script>

{#if loading}
  <div style="min-height:100vh;display:flex;align-items:center;
              justify-content:center">
    <p style="color:#0f766e">Loading...</p>
  </div>

{:else}
<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:40px">

  <!-- Header -->
  <div style="background:#0f766e;color:white;padding:40px 16px 24px">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div>
        <p style="color:#99f6e4;font-size:0.8rem">
          {stats?.facility ?? 'Health Facility'}
        </p>
        <h1 style="font-size:1.3rem;font-weight:700;margin:4px 0 0">
          Patient Monitoring
        </h1>
        <p style="color:#99f6e4;font-size:0.75rem;margin:4px 0 0">
          As of {stats?.as_of}
        </p>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#99f6e4;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
  </div>

  <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

    <!-- Stats row -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div style="background:white;border-radius:16px;padding:14px;
                  border:1px solid #f3f4f6;text-align:center">
        <p style="font-size:1.8rem;font-weight:700;color:#1f2937;margin:0">
          {stats?.total_patients ?? 0}
        </p>
        <p style="font-size:0.75rem;color:#9ca3af;margin:2px 0 0">
          Total patients
        </p>
      </div>
      <div style="background:#fef2f2;border-radius:16px;padding:14px;
                  border:1px solid #fecaca;text-align:center">
        <p style="font-size:1.8rem;font-weight:700;color:#dc2626;margin:0">
          {stats?.high_risk ?? 0}
        </p>
        <p style="font-size:0.75rem;color:#f87171;margin:2px 0 0">
          High risk today
        </p>
      </div>
      <div style="background:#fffbeb;border-radius:16px;padding:14px;
                  border:1px solid #fde68a;text-align:center">
        <p style="font-size:1.8rem;font-weight:700;color:#d97706;margin:0">
          {stats?.medium_risk ?? 0}
        </p>
        <p style="font-size:0.75rem;color:#fbbf24;margin:2px 0 0">
          Medium risk
        </p>
      </div>
      <div style="background:#f0fdf4;border-radius:16px;padding:14px;
                  border:1px solid #bbf7d0;text-align:center">
        <p style="font-size:1.8rem;font-weight:700;color:#16a34a;margin:0">
          {stats?.alerts_today ?? 0}
        </p>
        <p style="font-size:0.75rem;color:#4ade80;margin:2px 0 0">
          Alerts today
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div style="display:flex;background:#f3f4f6;border-radius:12px;padding:4px">
      {#each ['patients','alerts'] as t}
        <button onclick={() => tab = t}
          style="flex:1;padding:8px;border-radius:10px;border:none;
                 font-size:0.9rem;font-weight:500;cursor:pointer;
                 background:{tab === t ? 'white' : 'transparent'};
                 color:{tab === t ? '#0f766e' : '#6b7280'};
                 box-shadow:{tab === t ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'}">
          {t === 'patients' ? 'All patients' : 'Alerts'}
        </button>
      {/each}
    </div>

    <!-- Patients tab -->
    {#if tab === 'patients'}
      <div style="display:flex;flex-direction:column;gap:10px">
        {#each patients as p}
          {@const cc = conditionColors[p.condition] ?? conditionColors.cancer_remission}
          {@const rc = riskColors[p.risk_level] ?? riskColors.LOW}
          <div style="background:white;border-radius:16px;padding:14px;
                      border:1px solid #f3f4f6;
                      box-shadow:{p.risk_level === 'HIGH' ?
                        '0 2px 8px rgba(220,38,38,0.12)' :
                        '0 1px 3px rgba(0,0,0,0.04)'}">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start">
              <div>
                <p style="font-size:1rem;font-weight:600;
                          color:#1f2937;margin:0">
                  {p.full_name}
                </p>
                <p style="font-size:0.75rem;color:#9ca3af;margin:2px 0 6px">
                  Age {p.age} · Last check-in: {p.last_checkin}
                </p>
                <span style="background:{cc.bg};color:{cc.color};
                             border:1px solid {cc.border};border-radius:999px;
                             padding:2px 10px;font-size:0.72rem;font-weight:500">
                  {p.condition.replace(/_/g,' ')}
                </span>
              </div>
              <span style="background:{rc.bg};color:{rc.color};
                           border:1px solid {rc.border};border-radius:999px;
                           padding:4px 10px;font-size:0.75rem;font-weight:700">
                {p.risk_level}
              </span>
            </div>
          </div>
        {/each}
      </div>

    <!-- Alerts tab -->
    {:else}
      <div style="display:flex;flex-direction:column;gap:10px">
        {#each alerts as alert}
          {@const rc = riskColors[alert.risk_level] ?? riskColors.LOW}
          <div style="background:white;border-radius:16px;padding:14px;
                      border:2px solid {rc.border}">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:6px">
              <p style="font-size:1rem;font-weight:600;
                        color:#1f2937;margin:0">
                {alert.patient_name}
              </p>
              <span style="background:{rc.bg};color:{rc.color};
                           border:1px solid {rc.border};border-radius:999px;
                           padding:3px 10px;font-size:0.75rem;font-weight:700">
                {alert.risk_level}
              </span>
            </div>
            <p style="font-size:0.8rem;color:#6b7280;margin:0 0 4px">
              {alert.condition} · {alert.created_at}
            </p>
            <p style="font-size:0.85rem;color:#374151;margin:0">
              {alert.reason}
            </p>
          </div>
        {/each}
      </div>
    {/if}

    <!-- Trigger reminders -->
    <button onclick={trigger}
      style="width:100%;background:#f0fdfa;color:#0f766e;
             border:2px solid #99f6e4;border-radius:12px;
             padding:14px;font-size:0.9rem;font-weight:500;cursor:pointer">
      Send medication reminders now
    </button>

  </div>
</div>
{/if}