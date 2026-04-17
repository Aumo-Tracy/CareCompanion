<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patient   = $state(null);
  let reminders = $state([]);
  let loading   = $state(true);

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

  function logout() { clearUser(); goto('/'); }
</script>

{#if loading}
  <div style="min-height:100vh;display:flex;align-items:center;
              justify-content:center">
    <p style="color:#0f766e">Loading...</p>
  </div>
{:else}
<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:80px">

  <div style="background:#0d9488;color:white;padding:40px 16px 24px">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div>
        <p style="color:#99f6e4;font-size:0.85rem">Good morning,</p>
        <h1 style="font-size:1.6rem;font-weight:700;margin:2px 0">
          {patient?.full_name?.split(' ')[0] ?? 'Mary'}
        </h1>
        <p style="color:#99f6e4;font-size:0.8rem">
          {new Date().toLocaleDateString('en-UG',{
            weekday:'long',day:'numeric',month:'long'})}
        </p>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#99f6e4;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
    <div style="margin-top:12px;display:inline-flex;
                background:rgba(255,255,255,0.2);
                border-radius:999px;padding:4px 12px">
      <span style="font-size:0.85rem;font-weight:500">
        Gestational Diabetes
      </span>
    </div>
  </div>

  <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

    <!-- Risk badge — LOW -->
    <div style="border:2px solid #bbf7d0;border-radius:16px;
                padding:16px;background:#f0fdf4">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <p style="font-size:0.7rem;text-transform:uppercase;
                    color:#16a34a;opacity:0.7">Current risk level</p>
          <p style="font-size:2rem;font-weight:700;color:#16a34a;margin:4px 0 0">
            LOW
          </p>
        </div>
        <span style="font-size:2.5rem">✅</span>
      </div>
      <p style="font-size:0.85rem;color:#16a34a;margin-top:8px;opacity:0.85">
        You and baby are doing well. Keep monitoring your blood sugar.
      </p>
    </div>

    <!-- Metrics -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Blood sugar AM</p>
        <p style="font-size:1.1rem;font-weight:700;color:#16a34a;margin:4px 0 0">
          6.1 mmol/L
        </p>
        <p style="font-size:0.72rem;color:#4ade80">Normal ✓</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Fetal movement</p>
        <p style="font-size:1.1rem;font-weight:700;color:#16a34a;margin:4px 0 0">
          Active ✓
        </p>
        <p style="font-size:0.72rem;color:#4ade80">Today</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Weight this week</p>
        <p style="font-size:1.1rem;font-weight:700;color:#0f766e;margin:4px 0 0">
          +0.8 kg
        </p>
        <p style="font-size:0.72rem;color:#9ca3af">Normal</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Next ANC visit</p>
        <p style="font-size:1.1rem;font-weight:700;color:#0f766e;margin:4px 0 0">
          Thursday
        </p>
        <p style="font-size:0.72rem;color:#9ca3af">2 days away</p>
      </div>
    </div>

    <!-- Fetal movement prompt -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:1rem;font-weight:600;color:#1f2937;margin:0 0 4px">
        How is baby moving today?
      </h2>
      <p style="font-size:0.85rem;color:#6b7280;margin:0 0 12px">
        Report any changes immediately.
      </p>
      <div style="display:flex;flex-direction:column;gap:8px">
        {#each [
          {label:'Active — moving well', color:'#16a34a', bg:'#f0fdf4'},
          {label:'Less than usual',      color:'#d97706', bg:'#fffbeb'},
          {label:'Not moving at all',    color:'#dc2626', bg:'#fef2f2'},
        ] as opt}
          <button style="padding:12px;border-radius:10px;border:1px solid;
                         border-color:{opt.color}22;background:{opt.bg};
                         color:{opt.color};font-size:0.9rem;
                         cursor:pointer;text-align:left">
            {opt.label}
          </button>
        {/each}
      </div>
    </div>

    <button onclick={() => goto('/checkin')}
      style="width:100%;background:#0d9488;color:white;border:none;
             border-radius:12px;padding:14px;font-size:1rem;
             font-weight:500;cursor:pointer">
      Start daily check-in
    </button>

  </div>

  <div style="position:fixed;bottom:0;left:0;right:0;background:white;
              border-top:1px solid #f3f4f6;display:flex;max-width:480px;margin:0 auto">
    {#each [
      {label:'Home',    path:'/dashboard/gestational', icon:'🏠'},
      {label:'Check-in',path:'/checkin',              icon:'✅'},
      {label:'Chat',    path:'/chat',                 icon:'💬'},
      {label:'History', path:'/checkin',              icon:'📋'},
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