<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { clearUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let patient   = $state(null);
  let reminders = $state([]);
  let loading   = $state(true);

  const bpReadings = [168, 162, 160, 158, 155];

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
    <p style="color:#d97706">Loading...</p>
  </div>
{:else}
<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:80px">

  <div style="background:#d97706;color:white;padding:40px 16px 24px">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div>
        <p style="color:#fef3c7;font-size:0.85rem">Good morning,</p>
        <h1 style="font-size:1.6rem;font-weight:700;margin:2px 0">
          {patient?.full_name?.split(' ')[0] ?? 'Richard'}
        </h1>
        <p style="color:#fef3c7;font-size:0.8rem">
          {new Date().toLocaleDateString('en-UG',{
            weekday:'long',day:'numeric',month:'long'})}
        </p>
      </div>
      <button onclick={logout}
        style="background:none;border:none;color:#fef3c7;
               font-size:0.8rem;cursor:pointer;text-decoration:underline">
        Sign out
      </button>
    </div>
    <div style="margin-top:12px;display:inline-flex;
                background:rgba(255,255,255,0.2);
                border-radius:999px;padding:4px 12px">
      <span style="font-size:0.85rem;font-weight:500">Hypertension</span>
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
    </div>

    <!-- BP trend -->
    <div style="background:white;border-radius:16px;padding:16px;
                border:1px solid #f3f4f6">
      <h2 style="font-size:0.9rem;font-weight:600;color:#1f2937;margin:0 0 12px">
        Your BP this week (systolic)
      </h2>
      <div style="display:flex;align-items:flex-end;gap:8px;height:60px">
        {#each bpReadings as reading, i}
          <div style="display:flex;flex-direction:column;
                      align-items:center;flex:1;gap:4px">
            <p style="font-size:0.65rem;color:#9ca3af;margin:0">{reading}</p>
            <div style="width:100%;border-radius:4px;
                        background:{reading > 160 ? '#fca5a5' : '#fde68a'};
                        height:{((reading - 140) / 40) * 40 + 10}px">
            </div>
            <p style="font-size:0.6rem;color:#9ca3af;margin:0">
              {['M','T','W','T','F'][i]}
            </p>
          </div>
        {/each}
      </div>
      <p style="font-size:0.75rem;color:#9ca3af;margin:8px 0 0">
        Trending down — keep taking your medication.
      </p>
    </div>

    <!-- Metrics -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Last BP</p>
        <p style="font-size:1.1rem;font-weight:700;color:#d97706;margin:4px 0 0">
          158/98
        </p>
        <p style="font-size:0.72rem;color:#fbbf24">mmHg — elevated</p>
      </div>
      <div style="background:white;border-radius:16px;padding:16px;
                  border:1px solid #f3f4f6">
        <p style="font-size:0.75rem;color:#9ca3af">Medication</p>
        <p style="font-size:1.1rem;font-weight:700;color:#16a34a;margin:4px 0 0">
          Taken ✓
        </p>
        <p style="font-size:0.72rem;color:#4ade80">Today</p>
      </div>
    </div>

    <!-- Tip -->
    <div style="background:#fffbeb;border-radius:16px;padding:16px;
                border:1px solid #fde68a">
      <p style="font-size:0.9rem;color:#d97706;line-height:1.5;margin:0">
        Keep taking your medication and reduce salt in your food.
        Your blood pressure is slowly improving. 💪
      </p>
    </div>

    <button onclick={() => goto('/checkin')}
      style="width:100%;background:#d97706;color:white;border:none;
             border-radius:12px;padding:14px;font-size:1rem;
             font-weight:500;cursor:pointer">
      Start daily check-in
    </button>

  </div>

  <div style="position:fixed;bottom:0;left:0;right:0;background:white;
              border-top:1px solid #f3f4f6;display:flex;max-width:480px;margin:0 auto">
    {#each [
      {label:'Home',    path:'/dashboard/hypertension', icon:'🏠'},
      {label:'Check-in',path:'/checkin',               icon:'✅'},
      {label:'Chat',    path:'/chat',                  icon:'💬'},
      {label:'History', path:'/checkin',               icon:'📋'},
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