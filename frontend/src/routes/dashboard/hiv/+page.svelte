<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patient   = $state(null);
  let reminders = $state([]);
  let loading   = $state(true);

  const adherence = [
    {day:'Mon', taken:true},
    {day:'Tue', taken:true},
    {day:'Wed', taken:false},
    {day:'Thu', taken:true},
    {day:'Fri', taken:true},
    {day:'Sat', taken:false},
    {day:'Sun', taken:null},
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

  function logout() { clearUser(); goto('/'); }
</script>

{#if loading}
  <div style="min-height:100vh;display:flex;align-items:center;
              justify-content:center">
    <p style="color:#7c3aed">Loading...</p>
  </div>
{:else}
<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:80px">

  <div style="background:#7c3aed;color:white;padding:40px 16px 24px">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div>
        <p style="color:#ddd6fe;font-size:0.85rem">Good morning,</p>
        <h1 style="font-size:1.6rem;font-weight:700;margin:2px 0">
          {patient?.full_name?.split(' ')[0] ?? 'Grace'}
        </h1>
        <p style="color:#ddd6fe;font-size:0.8rem">
          {new Date().toLocaleDateString('en-UG',{
            weekday:'long',day:'numeric',month:'long'})}
        </p>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#ddd6fe;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
    <div style="margin-top:12px;display:inline-flex;
                background:rgba(255,255,255,0.2);
                border-radius:999px;padding:4px 12px">
      <span style="font-size:0.85rem;font-weight:500">HIV — ART Treatment</span>
    </div>
  </div>

  <div style="padding:16px;display:flex;flex-direction:column;gap:16px">

    <!-- Risk badge -->
    <div style="border:2px solid #fde68a;border-radius:16px;
                padding:16px;background:#fffbeb">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <p style="font-size:0.7rem;text-transform:uppercase;
                    color:#d97706;opacity:0.7">Current risk level</p>
          <p style="font-size:2rem;font-weight:700;color:#d97706;margin:4px 0 0">
            MEDIUM
          </p>
        </div>
        <span style="font-size:2.5rem">⚡</span>
      </div>
      <p style="font-size:0.85rem;color:#d97706;margin-top:8px;opacity:0.85">
        Please take your ART medication today. Missing doses matters.
      </p>
    </div>

    <!-- ART adherence tracker -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:0.9rem;font-weight:600;color:#1f2937;margin:0 0 12px">
        ART adherence this week
      </h2>
      <div style="display:flex;gap:8px;justify-content:space-between">
        {#each adherence as day}
          <div style="display:flex;flex-direction:column;
                      align-items:center;gap:4px">
            <div style="width:32px;height:32px;border-radius:50%;
                        background:{day.taken === true ? '#7c3aed' :
                          day.taken === false ? '#fecaca' : '#f3f4f6'};
                        display:flex;align-items:center;
                        justify-content:center;font-size:0.75rem;
                        color:{day.taken === true ? 'white' :
                          day.taken === false ? '#dc2626' : '#9ca3af'}">
              {day.taken === true ? '✓' : day.taken === false ? '✗' : '?'}
            </div>
            <p style="font-size:0.65rem;color:#9ca3af;margin:0">{day.day}</p>
          </div>
        {/each}
      </div>
    </div>

    <!-- Metrics -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">ART today</p>
        <p style="font-size:1.1rem;font-weight:700;color:#d97706;margin:4px 0 0">
          Not yet
        </p>
        <p style="font-size:0.72rem;color:#fbbf24">Take now</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Days since miss</p>
        <p style="font-size:1.1rem;font-weight:700;color:#dc2626;margin:4px 0 0">
          2 days
        </p>
        <p style="font-size:0.72rem;color:#f87171">Take today</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Next viral load</p>
        <p style="font-size:1.1rem;font-weight:700;color:#0f766e;margin:4px 0 0">
          3 weeks
        </p>
        <p style="font-size:0.72rem;color:#9ca3af">Stay on track</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Clinic follow-up</p>
        <p style="font-size:1.1rem;font-weight:700;color:#0f766e;margin:4px 0 0">
          Monday
        </p>
        <p style="font-size:0.72rem;color:#9ca3af">Next week</p>
      </div>
    </div>

    <!-- Reminder -->
    <div style="background:#f5f3ff;border-radius:16px;padding:16px;
                border:1px solid #ddd6fe">
      <p style="font-size:0.9rem;color:#7c3aed;line-height:1.5;margin:0">
        ART works best when taken every day at the same time.
        You are protecting yourself and those you love. 💜
      </p>
    </div>

    <!-- Check-in -->
    <button onclick={() => goto('/checkin')}
      style="width:100%;background:#7c3aed;color:white;border:none;
             border-radius:12px;padding:14px;font-size:1rem;
             font-weight:500;cursor:pointer">
      Start daily check-in
    </button>

  </div>

  <div style="position:fixed;bottom:0;left:0;right:0;background:white;
              border-top:1px solid #f3f4f6;display:flex;max-width:480px;margin:0 auto">
    {#each [
      {label:'Home',    path:'/dashboard/hiv', icon:'🏠'},
      {label:'Check-in',path:'/checkin',       icon:'✅'},
      {label:'Chat',    path:'/chat',          icon:'💬'},
      {label:'History', path:'/checkin',       icon:'📋'},
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