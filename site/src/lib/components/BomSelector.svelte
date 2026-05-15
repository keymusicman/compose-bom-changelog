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
    color: rgba(255,255,255,0.6);
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  select {
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 4px;
    padding: 0 26px 0 10px;
    height: 30px;
    font-size: 13px;
    font-family: inherit;
    background: rgba(255,255,255,0.08);
    color: #ffffff;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 12 12'%3E%3Cpath fill='rgba(255,255,255,0.6)' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
  }

  select:hover {
    background-color: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.35);
  }

  select:focus {
    outline: 2px solid var(--color-brand);
    outline-offset: 1px;
    border-color: var(--color-brand);
  }

  select option {
    background: #303134;
    color: #ffffff;
  }

  .arrow {
    color: rgba(255,255,255,0.4);
    font-size: 14px;
  }

  @media (max-width: 480px) {
    .bom-selector {
      flex-direction: column;
      align-items: stretch;
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
