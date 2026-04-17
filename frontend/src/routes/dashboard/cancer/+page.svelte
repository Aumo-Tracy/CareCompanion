<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patient      = $state(null);
  let reminders    = $state([]);
  let loading      = $state(true);
  let newSymptoms  = $state([]);
  let showSymptoms = $state(false);

  const symptoms = [
    'Unexplained lump',
    'Unusual bleeding',
    'Severe weight loss',
    'Persistent pain',
    'Extreme fatigue',
  ];

  onMount(async () => {
    try {
      const me  = await api.me();
      patient   = me;
      const rem = await api.reminders();
      reminders = rem.medications ?? [];
    } catch (e) {
      goto('/');
    } finally {
      loading = false;
    }
  });

  function toggleSymptom(s) {
    if (newSymptoms.includes(s)) {
      newSymptoms = newSymptoms.filter(x => x !== s);
    } else {
      newSymptoms = [...newSymptoms, s];
    }
  }

  function logout() { clearUser(); goto('/'); }
</script>

{#if loading}
  <div style="min-height:100vh;display:flex;align-items:center;
              justify-content:center">
    <p style="color:#6b7280">Loading...</p>
  </div>
{:else}
<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:80px">

  <div style="background:#4b5563;color:white;padding:40px 16px 24px">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div>
        <p style="color:#d1d5db;font-size:0.85rem">Good morning,</p>
        <h1 style="font-size:1.6rem;font-weight:700;margin:2px 0">
          {patient?.full_name?.split(' ')[0] ?? 'Tom'}
        </h1>
        <p style="color:#d1d5db;font-size:0.8rem">
          {new Date().toLocaleDateString('en-UG',{
            weekday:'long',day:'numeric',month:'long'})}
        </p>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#d1d5db;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
    <div style="margin-top:12px;display:inline-flex;
                background:rgba(255,255,255,0.2);
                border-radius:999px;padding:4px 12px">
      <span style="font-size:0.85rem;font-weight:500">
        Cancer — Remission
      </span>
    </div>
  </div>

  <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

    <!-- Encouragement -->
    <div style="background:#f0fdf4;border-radius:16px;padding:16px;
                border:2px solid #bbf7d0">
      <p style="font-size:1rem;font-weight:600;color:#16a34a;margin:0 0 4px">
        ✅ You are doing well
      </p>
      <p style="font-size:0.85rem;color:#16a34a;margin:0;opacity:0.85">
        Keep attending your follow-up appointments.
        Early detection keeps you protected.
      </p>
    </div>

    <!-- Metrics -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Last oncology visit</p>
        <p style="font-size:1.1rem;font-weight:700;color:#16a34a;margin:4px 0 0">
          3 weeks ago
        </p>
        <p style="font-size:0.72rem;color:#4ade80">On track</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Next follow-up</p>
        <p style="font-size:1.1rem;font-weight:700;color:#d97706;margin:4px 0 0">
          1 week
        </p>
        <p style="font-size:0.72rem;color:#fbbf24">Do not miss it</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Medication today</p>
        <p style="font-size:1.1rem;font-weight:700;color:#16a34a;margin:4px 0 0">
          Taken ✓
        </p>
        <p style="font-size:0.72rem;color:#4ade80">Well done</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Energy level</p>
        <p style="font-size:1.1rem;font-weight:700;color:#6b7280;margin:4px 0 0">
          Moderate
        </p>
        <p style="font-size:0.72rem;color:#9ca3af">Yesterday</p>
      </div>
    </div>

    <!-- How are you feeling -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0 0 12px">
        How are you feeling today?
      </h2>
      <div style="display:flex;flex-direction:column;gap:8px">
        <button onclick={() => goto('/checkin')}
          style="padding:14px;border-radius:12px;border:1px solid #bbf7d0;
                 background:#f0fdf4;color:#16a34a;font-size:0.95rem;
                 cursor:pointer;text-align:left">
          Good — feeling well
        </button>
        <button onclick={() => goto('/checkin')}
          style="padding:14px;border-radius:12px;border:1px solid #fde68a;
                 background:#fffbeb;color:#d97706;font-size:0.95rem;
                 cursor:pointer;text-align:left">
          Tired / Low energy
        </button>
        <button onclick={() => showSymptoms = !showSymptoms}
          style="padding:14px;border-radius:12px;border:1px solid #fecaca;
                 background:#fef2f2;color:#dc2626;font-size:0.95rem;
                 cursor:pointer;text-align:left">
          New symptom to report ⚠️
        </button>
      </div>

      {#if showSymptoms}
        <div style="margin-top:12px;display:flex;
                    flex-direction:column;gap:8px">
          <p style="font-size:0.85rem;color:#6b7280;margin:0">
            Select what you are experiencing:
          </p>
          {#each symptoms as s}
            <button onclick={() => toggleSymptom(s)}
              style="padding:10px 14px;border-radius:10px;border:2px solid;
                     border-color:{newSymptoms.includes(s) ? '#dc2626' : '#e5e7eb'};
                     background:{newSymptoms.includes(s) ? '#fef2f2' : 'white'};
                     color:{newSymptoms.includes(s) ? '#dc2626' : '#4b5563'};
                     font-size:0.85rem;cursor:pointer;text-align:left">
              {s}
            </button>
          {/each}
          {#if newSymptoms.length > 0}
            <button style="width:100%;background:#dc2626;color:white;
                           border:none;border-radius:10px;padding:12px;
                           font-size:0.9rem;font-weight:600;cursor:pointer">
              Report to clinic
            </button>
          {/if}
        </div>
      {/if}
    </div>

    <button onclick={() => goto('/checkin')}
      style="width:100%;background:#4b5563;color:white;border:none;
             border-radius:12px;padding:14px;font-size:1rem;
             font-weight:500;cursor:pointer">
      Start daily check-in
    </button>

  </div>

  <div style="position:fixed;bottom:0;left:0;right:0;background:white;
              border-top:1px solid #f3f4f6;display:flex;max-width:480px;margin:0 auto">
    {#each [
      {label:'Home',    path:'/dashboard/cancer', icon:'🏠'},
      {label:'Check-in',path:'/checkin',          icon:'✅'},
      {label:'Chat',    path:'/chat',             icon:'💬'},
      {label:'History', path:'/checkin',          icon:'📋'},
    ] as tab}
      <button onclick={() => goto(tab.path)}
        style="flex:1;padding:12px 0;display:flex;flex-direction:column;
               align-items:center;gap:2px;background:none;border:none;
               cursor:pointer;color:#9ca3af;font-size:0.7rem">
        <span style="font-size:1.3rem">{tab.icon}</span>
        {tab.label}
      </button>
    {/each}
  </div>

</div>
{/if}