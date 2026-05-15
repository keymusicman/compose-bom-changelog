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
    gap: 6px;
    flex-wrap: wrap;
  }

  .selector-group {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .label {
    font-size: 12px;
    font-weight: 500;
    color: var(--nav-text-secondary);
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  select {
    border: 1px solid var(--nav-control-border);
    border-radius: 4px;
    padding: 0 26px 0 10px;
    height: 30px;
    font-size: 13px;
    font-family: inherit;
    background-color: var(--nav-control-bg);
    background-image: var(--nav-chevron);
    color: var(--nav-text);
    appearance: none;
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
    transition: background-color 0.15s, border-color 0.15s;
  }

  select:hover {
    background-color: var(--nav-control-hover-bg);
    border-color: var(--nav-control-hover-border);
  }

  select:focus {
    outline: 2px solid var(--color-brand);
    outline-offset: 1px;
    border-color: var(--color-brand);
  }

  select option {
    background: var(--color-surface);
    color: var(--color-text);
  }

  .arrow {
    color: var(--nav-text-secondary);
    font-size: 14px;
  }

  @media (max-width: 480px) {
    .bom-selector {
      flex-direction: column;
      align-items: stretch;
      gap: 0px;
    }

    .selector-group {
      display: grid;
      grid-template-columns: 36px 1fr;
      align-items: center;
    }

    .arrow {
      transform: rotate(90deg);
    }

    select {
      width: 100%;
    }
  }
</style>
