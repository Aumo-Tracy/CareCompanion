<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patient   = $state(null);
  let reminders = $state([]);
  let loading   = $state(true);
  let riskLevel = $state('HIGH');

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

  function logout() {
    clearUser();
    goto('/');
  }
</script>

{#if loading}
  <div style="min-height:100vh;display:flex;align-items:center;
              justify-content:center;background:#f0fdfa">
    <p style="color:#0f766e;font-size:1.1rem">Loading...</p>
  </div>

{:else}
  <div style="min-height:100vh;background:#f9fafb;padding-bottom:80px;
              font-family:sans-serif;max-width:480px;margin:0 auto">

    <!-- Header -->
    <div style="background:#0f766e;color:white;padding:40px 16px 24px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <p style="color:#99f6e4;font-size:0.85rem">Good morning,</p>
          <h1 style="font-size:1.6rem;font-weight:700;margin:2px 0">
            {patient?.full_name?.split(' ')[0] ?? 'Sarah'}
          </h1>
          <p style="color:#99f6e4;font-size:0.8rem">
            {new Date().toLocaleDateString('en-UG', {
              weekday:'long', day:'numeric', month:'long'
            })}
          </p>
        </div>
        <button onclick={logout}
          style="color:#99f6e4;font-size:0.8rem;background:none;
                 border:none;cursor:pointer;text-decoration:underline">
          Sign out
        </button>
      </div>
      <div style="margin-top:12px;display:inline-flex;align-items:center;
                  background:rgba(255,255,255,0.2);border-radius:999px;
                  padding:4px 12px">
        <span style="font-size:0.85rem;font-weight:500">
          Eclampsia — High-Risk Pregnancy
        </span>
      </div>
    </div>

    <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

      <!-- Risk badge -->
      <div style="border:2px solid #fecaca;border-radius:16px;padding:16px;
                  background:#fef2f2">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <p style="font-size:0.7rem;text-transform:uppercase;
                      letter-spacing:0.05em;color:#ef4444;opacity:0.7">
              Current risk level
            </p>
            <p style="font-size:2rem;font-weight:700;color:#dc2626;margin:4px 0 0">
              {riskLevel}
            </p>
          </div>
          <span style="font-size:2.5rem">⚠️</span>
        </div>
        {#if riskLevel === 'HIGH'}
          <p style="font-size:0.85rem;color:#dc2626;margin-top:8px;opacity:0.85">
            Your caregiver has been notified. Please contact your midwife today.
          </p>
        {/if}
      </div>

      <!-- Metric cards — 2 column grid -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div style="background:white;border-radius:16px;padding:16px;
                    border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
          <p style="font-size:0.75rem;color:#9ca3af">Blood pressure</p>
          <p style="font-size:1.3rem;font-weight:700;color:#dc2626;margin:4px 0 0">
            162/105
          </p>
          <p style="font-size:0.72rem;color:#f87171">mmHg — high</p>
        </div>

        <div style="background:white;border-radius:16px;padding:16px;
                    border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
          <p style="font-size:0.75rem;color:#9ca3af">Fetal movement</p>
          <p style="font-size:1.3rem;font-weight:700;color:#16a34a;margin:4px 0 0">
            Active
          </p>
          <p style="font-size:0.72rem;color:#4ade80">Today</p>
        </div>

        <div style="background:white;border-radius:16px;padding:16px;
                    border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
          <p style="font-size:0.75rem;color:#9ca3af">Next ANC visit</p>
          <p style="font-size:1.3rem;font-weight:700;color:#dc2626;margin:4px 0 0">
            Overdue
          </p>
          <p style="font-size:0.72rem;color:#f87171">Book now</p>
        </div>

        <div style="background:white;border-radius:16px;padding:16px;
                    border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
          <p style="font-size:0.75rem;color:#9ca3af">Check-in streak</p>
          <p style="font-size:1.3rem;font-weight:700;color:#0f766e;margin:4px 0 0">
            4 days
          </p>
          <p style="font-size:0.72rem;color:#9ca3af">Keep going!</p>
        </div>
      </div>

      <!-- Check-in prompt -->
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
        <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0">
          How are you feeling today?
        </h2>
        <p style="font-size:0.85rem;color:#6b7280;margin:6px 0 12px">
          Your daily check-in helps us keep you safe.
        </p>
        <button onclick={() => goto('/checkin')}
          style="width:100%;background:#0f766e;color:white;border:none;
                 border-radius:12px;padding:14px;font-size:1rem;
                 font-weight:500;cursor:pointer">
          Start daily check-in
        </button>
      </div>

      <!-- Medications -->
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
        <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0 0 12px">
          Medications today
        </h2>
        {#if reminders.length === 0}
          <p style="font-size:0.85rem;color:#9ca3af">No medications loaded.</p>
        {:else}
          <div style="display:flex;flex-direction:column;gap:8px">
            {#each reminders as med}
              <div style="display:flex;justify-content:space-between;
                          align-items:center;border:1px solid #f3f4f6;
                          border-radius:12px;padding:12px">
                <div>
                  <p style="font-size:0.9rem;font-weight:500;color:#1f2937">
                    {med.name}
                  </p>
                  <p style="font-size:0.75rem;color:#9ca3af">{med.schedule_time}</p>
                </div>
                <div style="width:28px;height:28px;border-radius:50%;
                            border:2px solid #0f766e;display:flex;
                            align-items:center;justify-content:center;
                            color:#0f766e;font-size:0.85rem;cursor:pointer">
                  ✓
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Emergency button -->
      <button style="width:100%;background:#dc2626;color:white;border:none;
                     border-radius:16px;padding:18px;font-size:1.1rem;
                     font-weight:700;cursor:pointer">
        Call Midwife Now
      </button>

    </div>

    <!-- Bottom nav -->
    <div style="position:fixed;bottom:0;left:0;right:0;background:white;
                border-top:1px solid #f3f4f6;display:flex;
                max-width:480px;margin:0 auto">
      {#each [
        { label:'Home',     path:'/dashboard/eclampsia', icon:'🏠' },
        { label:'Check-in', path:'/checkin',             icon:'✅' },
        { label:'Chat',     path:'/chat',                icon:'💬' },
        { label:'History',  path:'/checkin',             icon:'📋' },
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