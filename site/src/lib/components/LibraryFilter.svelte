<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let libraries: string[]
  export let selected: Set<string>
  export let showUnchanged: boolean

  const dispatch = createEventDispatcher<{
    change: { selected: Set<string>; showUnchanged: boolean }
  }>()

  let open = false

  function toggleLibrary(group: string) {
    const next = new Set(selected)
    if (next.has(group)) {
      next.delete(group)
    } else {
      next.add(group)
    }
    dispatch('change', { selected: next, showUnchanged })
  }

  function toggleUnchanged() {
    dispatch('change', { selected, showUnchanged: !showUnchanged })
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false
  }

  function handleOutsideClick(e: MouseEvent) {
    const target = e.target as HTMLElement
    if (!target.closest('.filter-root')) open = false
  }

  $: activeCount = selected.size
  $: label = activeCount === libraries.length ? 'Filter' : `Filter (${activeCount}/${libraries.length})`
</script>

<svelte:window on:keydown={handleKeydown} on:click={handleOutsideClick} />

<div class="filter-root">
  <button
    class="filter-btn"
    class:active={activeCount !== libraries.length || showUnchanged}
    on:click|stopPropagation={() => (open = !open)}
    aria-expanded={open}
    aria-haspopup="listbox"
  >
    {label}
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
      <path fill="currentColor" d="M6 8L1 3h10z" />
    </svg>
  </button>

  {#if open}
    <div class="popover" role="listbox" aria-multiselectable="true">
      {#each libraries as group}
        <label class="option">
          <input
            type="checkbox"
            checked={selected.has(group)}
            on:change={() => toggleLibrary(group)}
          />
          <span>{group.replace('androidx.', '')}</span>
        </label>
      {/each}

      <div class="divider"></div>

      <label class="option">
        <input type="checkbox" checked={showUnchanged} on:change={toggleUnchanged} />
        <span>Show unchanged</span>
      </label>
    </div>
  {/if}
</div>

<style>
  .filter-root {
    position: relative;
  }

  .filter-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 4px;
    padding: 0 10px;
    height: 30px;
    font-size: 13px;
    font-family: inherit;
    background: rgba(255,255,255,0.08);
    color: #ffffff;
    white-space: nowrap;
    transition: background 0.15s, border-color 0.15s;
  }

  .filter-btn:hover {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.35);
  }

  .filter-btn.active {
    border-color: var(--color-brand);
    color: var(--color-brand);
  }

  .popover {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    z-index: 100;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    min-width: 220px;
    padding: 8px 0;
  }

  .option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 16px;
    cursor: pointer;
    font-size: 13px;
    color: var(--color-text);
  }

  .option:hover {
    background: var(--color-surface);
  }

  .option input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--color-accent);
    cursor: pointer;
    flex-shrink: 0;
  }

  .divider {
    height: 1px;
    background: var(--color-border);
    margin: 6px 0;
  }

  @media (max-width: 480px) {
    .popover {
      right: auto;
      left: 0;
      width: calc(100vw - 40px);
    }
  }
</style>
