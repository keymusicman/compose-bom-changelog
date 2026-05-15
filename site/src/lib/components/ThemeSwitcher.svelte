<script lang="ts">
  import { onMount } from 'svelte'

  type Theme = 'system' | 'light' | 'dark'
  const order: Theme[] = ['system', 'light', 'dark']

  let theme: Theme = 'system'

  onMount(() => {
    theme = (localStorage.getItem('theme') as Theme) ?? 'system'
  })

  function cycle() {
    theme = order[(order.indexOf(theme) + 1) % order.length]
    if (theme === 'system') {
      localStorage.removeItem('theme')
      delete document.documentElement.dataset.theme
    } else {
      localStorage.setItem('theme', theme)
      document.documentElement.dataset.theme = theme
    }
  }
</script>

<button class="theme-btn" on:click={cycle} title="Theme: {theme}" aria-label="Switch theme ({theme})">
  {#if theme === 'light'}
    <!-- Sun -->
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
    </svg>
  {:else if theme === 'dark'}
    <!-- Moon -->
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  {:else}
    <!-- Monitor (system) -->
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <rect x="2" y="3" width="20" height="14" rx="2"/>
      <path d="M8 21h8M12 17v4"/>
    </svg>
  {/if}
</button>

<style>
  .theme-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border: 1px solid var(--nav-control-border);
    border-radius: 4px;
    background: var(--nav-control-bg);
    color: var(--nav-text);
    padding: 0;
    flex-shrink: 0;
    transition: background 0.15s, border-color 0.15s;
  }

  .theme-btn:hover {
    background: var(--nav-control-hover-bg);
    border-color: var(--nav-control-hover-border);
    color: var(--nav-text);
  }
</style>
