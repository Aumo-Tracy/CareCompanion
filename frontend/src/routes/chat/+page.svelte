<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { goto } from '$app/navigation';

  let messages  = $state([
    { role: 'assistant', content: 'Hello! How are you feeling today? I am here to help.' }
  ]);
  let input     = $state('');
  let sending   = $state(false);
  let container;

  async function send() {
    if (!input.trim() || sending) return;
    const text = input.trim();
    input      = '';
    sending    = true;

    messages = [...messages, { role: 'user', content: text }];
    scrollBottom();

    try {
      const res = await api.chat(text);
      messages  = [...messages, { role: 'assistant', content: res.reply }];
    } catch (e) {
      messages = [...messages,
        { role: 'assistant', content: 'Sorry, I could not connect. Please try again.' }
      ];
    } finally {
      sending = false;
      scrollBottom();
    }
  }

  function scrollBottom() {
    setTimeout(() => {
      if (container) container.scrollTop = container.scrollHeight;
    }, 50);
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }
</script>

<div style="min-height:100vh;background:#f9fafb;font-family:sans-serif;
            max-width:480px;margin:0 auto;display:flex;flex-direction:column">

  <!-- Header -->
  <div style="background:#0f766e;color:white;padding:40px 16px 16px;
              display:flex;align-items:center;gap:12px;flex-shrink:0">
    <button onclick={() => goto('/dashboard/eclampsia')}
      style="background:none;border:none;color:white;
             font-size:1.4rem;cursor:pointer;padding:0">
      ←
    </button>
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:36px;height:36px;border-radius:50%;
                  background:rgba(255,255,255,0.2);display:flex;
                  align-items:center;justify-content:center;font-size:1.1rem">
        💚
      </div>
      <div>
        <p style="font-weight:600;margin:0;font-size:1rem">CareCompanion</p>
        <p style="font-size:0.75rem;color:#99f6e4;margin:0">Here for you 24/7</p>
      </div>
    </div>
  </div>

  <!-- Messages -->
  <div bind:this={container}
    style="flex:1;overflow-y:auto;padding:16px;
           display:flex;flex-direction:column;gap:10px">
    {#each messages as msg}
      <div style="display:flex;
                  justify-content:{msg.role === 'user' ? 'flex-end' : 'flex-start'}">
        <div style="max-width:80%;padding:12px 16px;border-radius:16px;
                    font-size:0.9rem;line-height:1.5;
                    background:{msg.role === 'user' ? '#0f766e' : 'white'};
                    color:{msg.role === 'user' ? 'white' : '#1f2937'};
                    border:{msg.role === 'user' ? 'none' : '1px solid #f3f4f6'};
                    border-bottom-right-radius:{msg.role === 'user' ? '4px' : '16px'};
                    border-bottom-left-radius:{msg.role === 'user' ? '16px' : '4px'}">
          {msg.content}
        </div>
      </div>
    {/each}
    {#if sending}
      <div style="display:flex;justify-content:flex-start">
        <div style="background:white;border:1px solid #f3f4f6;
                    border-radius:16px;border-bottom-left-radius:4px;
                    padding:12px 16px;color:#9ca3af;font-size:0.9rem">
          Typing...
        </div>
      </div>
    {/if}
  </div>

  <!-- Emergency button -->
  <div style="padding:0 16px 8px;flex-shrink:0">
    <button style="width:100%;background:#fef2f2;color:#dc2626;
                   border:2px solid #fecaca;border-radius:12px;
                   padding:10px;font-size:0.9rem;font-weight:600;cursor:pointer">
      ⚠️ Call Midwife Now
    </button>
  </div>

  <!-- Input -->
  <div style="padding:8px 16px 24px;background:white;
              border-top:1px solid #f3f4f6;flex-shrink:0;
              display:flex;gap:8px;align-items:flex-end">
    <textarea
      bind:value={input}
      onkeydown={handleKey}
      placeholder="Type a message..."
      rows="1"
      style="flex:1;border:1px solid #e5e7eb;border-radius:12px;
             padding:10px 14px;font-size:0.9rem;resize:none;
             font-family:sans-serif;outline:none">
    </textarea>
    <button onclick={send} disabled={sending}
      style="background:#0f766e;color:white;border:none;
             border-radius:12px;padding:10px 16px;
             font-size:0.9rem;cursor:pointer;
             opacity:{sending ? 0.6 : 1};white-space:nowrap">
      Send
    </button>
  </div>

</div>