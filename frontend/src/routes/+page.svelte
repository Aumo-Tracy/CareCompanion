<script>
  import { api } from '$lib/api.js';
  import { setUser } from '$lib/stores.js';
  import { goto } from '$app/navigation';

  let email   = $state('');
  let password = $state('');
  let loading  = $state(false);
  let error    = $state('');

  const demoUsers = [
    { label: 'Patient (Eclampsia)', email: 'patient@demo.com' },
    { label: 'Caregiver',          email: 'caregiver@demo.com' },
    { label: 'Facility Admin',     email: 'admin@demo.com' },
    { label: 'Patient (Diabetes)', email: 'diabetes@demo.com' },
    { label: 'Patient (HIV)',      email: 'hiv@demo.com' },
  ];

  async function login() {
    if (!email) return;
    loading = true;
    error   = '';
    try {
      const res = await api.login(email, password || 'demo');
      if (res.token) {
        setUser(
          {
            user_id:   res.user_id,
            full_name: res.full_name,
            role:      res.role,
            condition: res.condition,
          },
          res.token
        );
        goto(res.redirect_to);
      } else {
        error = res.detail ?? 'Login failed';
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function quickLogin(demoEmail) {
    email    = demoEmail;
    password = 'demo';
    login();
  }
</script>

<div class="min-h-screen bg-teal-50 flex flex-col items-center justify-center px-4">

  <div class="text-center mb-8">
    <div class="inline-flex items-center justify-center w-16 h-16 bg-teal-600 rounded-2xl mb-4">
      <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
      </svg>
    </div>
    <h1 class="text-3xl font-bold text-teal-800">CareCompanion</h1>
    <p class="text-teal-600 mt-1">Your daily health companion</p>
  </div>

  <div class="bg-white rounded-2xl shadow-sm w-full max-w-sm p-6">

    {#if error}
      <div class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">
        {error}
      </div>
    {/if}

    <div class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="your@email.com"
          class="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-400"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          placeholder="••••••••"
          class="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-400"
        />
      </div>

      <button
        onclick={login}
        disabled={loading}
        class="w-full bg-teal-600 text-white rounded-xl py-3 font-medium text-lg hover:bg-teal-700 transition disabled:opacity-50"
      >
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </div>

    <div class="mt-6">
      <p class="text-xs text-gray-400 text-center mb-3">
        Demo — tap to login instantly
      </p>
      <div class="space-y-2">
        {#each demoUsers as u}
          <button
            onclick={() => quickLogin(u.email)}
            class="w-full text-left border border-gray-100 rounded-xl px-4 py-2 text-sm text-gray-600 hover:bg-teal-50 hover:border-teal-200 transition"
          >
            {u.label}
          </button>
        {/each}
      </div>
    </div>

  </div>

  <p class="text-xs text-teal-500 mt-6">
    Powered by AI. Built for Uganda.
  </p>

</div>