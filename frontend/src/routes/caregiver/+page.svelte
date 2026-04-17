<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patientData = $state(null);
  let alerts      = $state([]);
  let loading     = $state(true);
  let support     = $state('');

  const riskColors = {
    HIGH:   { bg: '#fef2f2', border: '#fecaca', color: '#dc2626' },
    MEDIUM: { bg: '#fffbeb', border: '#fde68a', color: '#d97706' },
    LOW:    { bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a' },
  };

  onMount(async () => {
    try {
      const [p, a] = await Promise.all([
        api.caregiverPatient(),
        api.caregiverAlerts(),
      ]);
      patientData = p;
      alerts      = a;
    } catch (e) {
      goto('/');
    } finally {
      loading = false;
    }
  });

  async function resolve(id) {
    await api.resolveAlert(id);
    alerts = alerts.map(a => a.id === id ? { ...a, is_resolved: true } : a);
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
    <div style="display:flex;justify-content:space-between">
      <div>
        <p style="color:#99f6e4;font-size:0.85rem">Caregiver dashboard</p>
        <h1 style="font-size:1.4rem;font-weight:700;margin:4px 0 0">
          Hello, Mukasa John
        </h1>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#99f6e4;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
    <p style="color:#99f6e4;font-size:0.8rem;margin:8px 0 0">
      Thank you for supporting {patientData?.patient_name}'s health journey.
    </p>
  </div>

  <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

    <!-- Patient status card -->
    {#if patientData}
      {@const rs = riskColors[patientData.risk_level] ?? riskColors.LOW}
      <div style="background:white;border-radius:16px;padding:16px;
                  border:2px solid {rs.border};
                  box-shadow:0 1px 3px rgba(0,0,0,0.06)">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start">
          <div>
            <p style="font-size:1.1rem;font-weight:700;color:#1f2937;margin:0">
              {patientData.patient_name}
            </p>
            <p style="font-size:0.8rem;color:#6b7280;margin:2px 0 0">
              {patientData.condition} · Last check-in: {patientData.last_checkin}
            </p>
          </div>
          <span style="background:{rs.bg};color:{rs.color};
                       border:1px solid {rs.border};border-radius:999px;
                       padding:4px 10px;font-size:0.75rem;font-weight:700">
            {patientData.risk_level}
          </span>
        </div>
        <div style="margin-top:12px;display:flex;gap:8px">
          <button style="flex:1;background:#0f766e;color:white;border:none;
                         border-radius:10px;padding:10px;font-size:0.85rem;
                         font-weight:500;cursor:pointer">
            Call {patientData.patient_name?.split(' ')[0]}
          </button>
          <button onclick={() => goto('/dashboard/eclampsia')}
            style="flex:1;background:white;color:#0f766e;
                   border:2px solid #0f766e;border-radius:10px;
                   padding:10px;font-size:0.85rem;cursor:pointer">
            View report
          </button>
        </div>
      </div>
    {/if}

    <!-- Weekly support check-in -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0 0 4px">
        Can you support {patientData?.patient_name?.split(' ')[0]} this week?
      </h2>
      <p style="font-size:0.8rem;color:#6b7280;margin:0 0 12px">
        Your support matters to their recovery.
      </p>
      <div style="display:flex;flex-direction:column;gap:8px">
        {#each [
          { label: 'Yes, fully',      value: 'full',    color: '#16a34a' },
          { label: 'Partially',       value: 'partial', color: '#d97706' },
          { label: 'I need help too', value: 'help',    color: '#7c3aed' },
        ] as opt}
          <button
            onclick={() => support = opt.value}
            style="padding:14px;border-radius:12px;border:2px solid;
                   border-color:{support === opt.value ? opt.color : '#e5e7eb'};
                   background:{support === opt.value ? '#f9fafb' : 'white'};
                   color:{support === opt.value ? opt.color : '#4b5563'};
                   font-size:0.95rem;font-weight:500;
                   cursor:pointer;text-align:left">
            {opt.label}
          </button>
        {/each}
        {#if support === 'help'}
          <div style="background:#f5f3ff;border-radius:12px;padding:12px;
                      border:1px solid #ddd6fe">
            <p style="font-size:0.85rem;color:#7c3aed;margin:0">
              We will connect you with a community health worker.
            </p>
          </div>
        {/if}
      </div>
    </div>

    <!-- Recent alerts -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0 0 12px">
        Recent alerts
      </h2>
      {#if alerts.length === 0}
        <p style="font-size:0.85rem;color:#9ca3af">No alerts.</p>
      {:else}
        <div style="display:flex;flex-direction:column;gap:10px">
          {#each alerts as alert}
            {@const ac = riskColors[alert.risk_level] ?? riskColors.LOW}
            <div style="border:1px solid {ac.border};border-radius:12px;
                        padding:12px;background:{ac.bg}">
              <div style="display:flex;justify-content:space-between;
                          align-items:center">
                <span style="font-size:0.75rem;font-weight:700;
                              color:{ac.color}">{alert.risk_level}</span>
                <span style="font-size:0.7rem;color:#9ca3af">
                  {alert.created_at}
                </span>
              </div>
              <p style="font-size:0.85rem;color:#374151;margin:4px 0 0">
                {alert.reason}
              </p>
              {#if !alert.is_resolved}
                <button onclick={() => resolve(alert.id)}
                  style="margin-top:8px;background:white;
                         border:1px solid {ac.border};color:{ac.color};
                         border-radius:8px;padding:6px 12px;
                         font-size:0.8rem;cursor:pointer">
                  Mark resolved
                </button>
              {:else}
                <p style="font-size:0.75rem;color:#9ca3af;margin:6px 0 0">
                  ✓ Resolved
                </p>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <p style="text-align:center;font-size:0.8rem;color:#9ca3af">
      You are not alone in this. CareCompanion is here for both of you.
    </p>

  </div>
</div>
{/if}