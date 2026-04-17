<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { goto } from '$app/navigation';

  let step         = $state(1);
  let questions    = $state(null);
  let loading      = $state(true);
  let submitting   = $state(false);
  let result       = $state(null);

  let selectedSymptoms = $state([]);
  let missedDoses      = $state(0);
  let extraData        = $state({});

  const riskStyles = {
    HIGH:   { bg: '#fef2f2', border: '#fecaca', color: '#dc2626', icon: '⚠️' },
    MEDIUM: { bg: '#fffbeb', border: '#fde68a', color: '#d97706', icon: '⚡' },
    LOW:    { bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a', icon: '✅' },
  };

  let resultStyle = $derived(
    result ? (riskStyles[result.risk_level] ?? riskStyles.LOW) : riskStyles.LOW
  );

  onMount(async () => {
    try {
      const q = await api.checkinQuestions();
      questions = q;
    } catch (e) {
      goto('/');
    } finally {
      loading = false;
    }
  });

  function toggleSymptom(symptom) {
    if (selectedSymptoms.includes(symptom)) {
      selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);
    } else {
      selectedSymptoms = [...selectedSymptoms, symptom];
    }
  }

  function formatSymptom(s) {
    return s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  async function submit() {
    submitting = true;
    try {
      const res = await api.submitCheckin({
        symptoms:     selectedSymptoms,
        missed_doses: missedDoses,
        extra_data:   extraData,
      });
      result = res;
      step   = 4;
    } catch (e) {
      alert('Submission failed. Please try again.');
    } finally {
      submitting = false;
    }
  }
</script>

<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;padding-bottom:40px">

  <!-- Header -->
  <div style="background:#0f766e;color:white;padding:40px 16px 20px;
              display:flex;align-items:center;gap:12px">
    <button
      onclick={() => step > 1 && step < 4 ? step-- : goto('/dashboard/eclampsia')}
      style="background:none;border:none;color:white;font-size:1.4rem;
             cursor:pointer;padding:0">
      ←
    </button>
    <div>
      <h1 style="font-size:1.2rem;font-weight:700;margin:0">Daily Check-in</h1>
      {#if step < 4}
        <p style="font-size:0.8rem;color:#99f6e4;margin:2px 0 0">
          Step {step} of 3
        </p>
      {/if}
    </div>
  </div>

  <!-- Step progress bar -->
  {#if step < 4}
    <div style="display:flex;gap:6px;padding:16px 16px 0">
      {#each [1, 2, 3] as s}
        <div style="flex:1;height:4px;border-radius:2px;
                    background:{s <= step ? '#0f766e' : '#e5e7eb'}">
        </div>
      {/each}
    </div>
  {/if}

  <div style="padding:16px">

    <!-- Step 1 — Symptoms -->
    {#if step === 1}
      <div style="display:flex;flex-direction:column;gap:16px">

        <div>
          <h2 style="font-size:1.1rem;font-weight:600;color:#1f2937;margin:0">
            How are you feeling today?
          </h2>
          <p style="font-size:0.85rem;color:#6b7280;margin:6px 0 0">
            Tap everything you are feeling right now.
          </p>
        </div>

        {#if loading}
          <p style="color:#6b7280">Loading questions...</p>
        {:else}
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            {#each (questions?.questions?.symptoms ?? []) as symptom}
              <button
                onclick={() => toggleSymptom(symptom)}
                style="padding:14px 10px;border-radius:12px;border:2px solid;
                       border-color:{selectedSymptoms.includes(symptom) ? '#0f766e' : '#e5e7eb'};
                       background:{selectedSymptoms.includes(symptom) ? '#f0fdfa' : 'white'};
                       color:{selectedSymptoms.includes(symptom) ? '#0f766e' : '#4b5563'};
                       font-size:0.85rem;
                       font-weight:{selectedSymptoms.includes(symptom) ? '600' : '400'};
                       cursor:pointer;text-align:center;
                       box-shadow:0 1px 2px rgba(0,0,0,0.04)">
                {formatSymptom(symptom)}
              </button>
            {/each}
            <button
              onclick={() => selectedSymptoms = []}
              style="padding:14px 10px;border-radius:12px;border:2px solid;
                     border-color:{selectedSymptoms.length === 0 ? '#0f766e' : '#e5e7eb'};
                     background:{selectedSymptoms.length === 0 ? '#f0fdfa' : 'white'};
                     color:{selectedSymptoms.length === 0 ? '#0f766e' : '#4b5563'};
                     font-size:0.85rem;cursor:pointer;text-align:center">
              None of these
            </button>
          </div>
        {/if}

        <button
          onclick={() => step = 2}
          style="width:100%;background:#0f766e;color:white;border:none;
                 border-radius:12px;padding:14px;font-size:1rem;
                 font-weight:500;cursor:pointer;margin-top:8px">
          Next →
        </button>

      </div>

    <!-- Step 2 — Medication -->
    {:else if step === 2}
      <div style="display:flex;flex-direction:column;gap:16px">

        <div>
          <h2 style="font-size:1.1rem;font-weight:600;color:#1f2937;margin:0">
            Did you take your medication today?
          </h2>
          <p style="font-size:0.85rem;color:#6b7280;margin:6px 0 0">
            {questions?.questions?.medication_label ?? 'your medication'}
          </p>
        </div>

        <div style="display:flex;flex-direction:column;gap:10px">
          {#each [
            { label: 'Yes — all taken',    value: 0, color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
            { label: 'Some — missed some', value: 1, color: '#d97706', bg: '#fffbeb', border: '#fde68a' },
            { label: 'No — not taken',     value: 2, color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
          ] as opt}
            <button
              onclick={() => missedDoses = opt.value}
              style="padding:18px;border-radius:12px;border:2px solid;
                     border-color:{missedDoses === opt.value ? opt.border : '#e5e7eb'};
                     background:{missedDoses === opt.value ? opt.bg : 'white'};
                     color:{missedDoses === opt.value ? opt.color : '#4b5563'};
                     font-size:1rem;font-weight:500;cursor:pointer;text-align:left">
              {opt.label}
            </button>
          {/each}
        </div>

        <button
          onclick={() => step = 3}
          style="width:100%;background:#0f766e;color:white;border:none;
                 border-radius:12px;padding:14px;font-size:1rem;
                 font-weight:500;cursor:pointer;margin-top:8px">
          Next →
        </button>

      </div>

    <!-- Step 3 — Fetal movement -->
    {:else if step === 3}
      <div style="display:flex;flex-direction:column;gap:16px">

        <div>
          <h2 style="font-size:1.1rem;font-weight:600;color:#1f2937;margin:0">
            How is your baby moving today?
          </h2>
          <p style="font-size:0.85rem;color:#6b7280;margin:6px 0 0">
            Baby movement is an important sign of health.
          </p>
        </div>

        <div style="display:flex;flex-direction:column;gap:10px">
          {#each [
            { label: 'Moving well',           value: 'active', color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
            { label: 'Moving less than usual', value: 'less',  color: '#d97706', bg: '#fffbeb', border: '#fde68a' },
            { label: 'Not moving at all',      value: 'none',  color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
          ] as opt}
            <button
              onclick={() => extraData = { ...extraData, fetal_movement: opt.value }}
              style="padding:18px;border-radius:12px;border:2px solid;
                     border-color:{extraData.fetal_movement === opt.value ? opt.border : '#e5e7eb'};
                     background:{extraData.fetal_movement === opt.value ? opt.bg : 'white'};
                     color:{extraData.fetal_movement === opt.value ? opt.color : '#4b5563'};
                     font-size:1rem;font-weight:500;cursor:pointer;text-align:left">
              {opt.label}
            </button>
          {/each}
        </div>

        <button
          onclick={submit}
          disabled={submitting}
          style="width:100%;background:#0f766e;color:white;border:none;
                 border-radius:12px;padding:14px;font-size:1rem;
                 font-weight:500;cursor:pointer;margin-top:8px;
                 opacity:{submitting ? 0.6 : 1}">
          {submitting ? 'Submitting...' : 'Submit check-in'}
        </button>

      </div>

    <!-- Step 4 — Result -->
    {:else if step === 4 && result}
      <div style="display:flex;flex-direction:column;gap:16px">

        <div style="border:2px solid {resultStyle.border};border-radius:16px;
                    padding:20px;background:{resultStyle.bg};text-align:center">
          <div style="font-size:3rem">{resultStyle.icon}</div>
          <p style="font-size:0.75rem;text-transform:uppercase;
                    letter-spacing:0.05em;color:{resultStyle.color};
                    opacity:0.7;margin:8px 0 4px">
            Risk level
          </p>
          <p style="font-size:2.2rem;font-weight:700;
                    color:{resultStyle.color};margin:0">
            {result.risk_level}
          </p>
          <p style="font-size:0.85rem;color:{resultStyle.color};
                    margin:8px 0 0;opacity:0.85">
            Score: {result.risk_score}/100
          </p>
        </div>

        <div style="background:white;border-radius:16px;padding:16px;
                    border:1px solid #f3f4f6">
          <p style="font-size:0.75rem;color:#9ca3af;
                    text-transform:uppercase;margin:0 0 6px">Why</p>
          <p style="font-size:0.9rem;color:#374151;margin:0">
            {result.reason}
          </p>
        </div>

        <div style="background:#f0fdfa;border-radius:16px;padding:16px;
                    border:1px solid #99f6e4">
          <p style="font-size:0.95rem;color:#0f766e;line-height:1.5;margin:0">
            {result.message}
          </p>
        </div>

        {#if result.risk_level === 'HIGH'}
          <button style="width:100%;background:#dc2626;color:white;border:none;
                         border-radius:16px;padding:18px;font-size:1.1rem;
                         font-weight:700;cursor:pointer">
            Call Midwife Now
          </button>
        {/if}

        <button
          onclick={() => goto('/dashboard/eclampsia')}
          style="width:100%;background:#0f766e;color:white;border:none;
                 border-radius:12px;padding:14px;font-size:1rem;
                 font-weight:500;cursor:pointer">
          Back to dashboard
        </button>

      </div>
    {/if}

  </div>
</div>