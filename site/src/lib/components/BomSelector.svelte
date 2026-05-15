<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import type { BomData } from '$lib/types'

  export let data: BomData
  export let fromBom: string
  export let toBom: string

  $: sortedVersions = Object.keys(data.bom_versions).sort().reverse()

  const dispatch = createEventDispatcher<{ change: { fromBom: string; toBom: string } }>()

  function handleFromChange(e: Event) {
    const value = (e.target as HTMLSelectElement).value
    dispatch('change', { fromBom: value, toBom })
  }

  function handleToChange(e: Event) {
    const value = (e.target as HTMLSelectElement).value
    dispatch('change', { fromBom, toBom: value })
  }
</script>

<div class="bom-selector">
  <label class="selector-group">
    <span class="label">From</span>
    <select value={fromBom} on:change={handleFromChange}>
      {#each sortedVersions as version}
        <option value={version}>{version}</option>
      {/each}
    </select>
  </label>

  <span class="arrow" aria-hidden="true">→</span>

  <label class="selector-group">
    <span class="label">To</span>
    <select value={toBom} on:change={handleToChange}>
      {#each sortedVersions as version}
        <option value={version}>{version}</option>
      {/each}
    </select>
  </label>
</div>

<style>
  .bom-selector {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .selector-group {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .label {
    font-size: 14px;
    color: var(--color-text-secondary);
    white-space: nowrap;
  }

  select {
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 6px 28px 6px 10px;
    font-size: 14px;
    background: var(--color-bg);
    color: var(--color-text);
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
  }

  select:focus {
    outline: 2px solid var(--color-accent);
    outline-offset: 1px;
  }

  .arrow {
    color: var(--color-text-secondary);
    font-size: 16px;
  }

  @media (max-width: 480px) {
    .bom-selector {
      flex-direction: column;
      align-items: flex-start;
    }

    .arrow {
      transform: rotate(90deg);
    }

    select {
      width: 100%;
    }
  }
</style>
