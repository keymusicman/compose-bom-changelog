<script lang="ts">
  import { page } from '$app/stores'
  import { goto } from '$app/navigation'
  import type { PageData } from './$types'
  import { computeDiff } from '$lib/diff'
  import BomSelector from '$lib/components/BomSelector.svelte'
  import LibraryFilter from '$lib/components/LibraryFilter.svelte'
  import WhatsNewCard from '$lib/components/WhatsNewCard.svelte'
  import LibraryDiff from '$lib/components/LibraryDiff.svelte'

  export let data: PageData

  $: sortedVersions = Object.keys(data.data.bom_versions).sort()

  $: defaultTo = sortedVersions.at(-1) ?? ''
  $: defaultFrom = sortedVersions.at(-2) ?? ''

  let fromBom = ''
  let toBom = ''

  // Keep fromBom/toBom in sync with URL (handles back/forward navigation)
  $: {
    const url = $page.url
    if (url) {
      const urlFrom = url.searchParams.get('from')
      const urlTo = url.searchParams.get('to')
      if (urlFrom && urlTo) {
        fromBom = urlFrom
        toBom = urlTo
      } else if (defaultFrom && defaultTo && !fromBom) {
        fromBom = defaultFrom
        toBom = defaultTo
      }
    }
  }

  function handleSelectorChange(e: CustomEvent<{ fromBom: string; toBom: string }>) {
    fromBom = e.detail.fromBom
    toBom = e.detail.toBom
    const params = new URLSearchParams({ from: fromBom, to: toBom })
    goto(`?${params}`, { replaceState: false, keepFocus: true })
  }

  $: diff = fromBom && toBom ? computeDiff(fromBom, toBom, data.data) : null

  $: allLibraries = diff ? [...diff.changed.map(c => c.group), ...diff.unchanged].sort() : []
  let selected: Set<string> = new Set()
  let showUnchanged = false

  $: if (allLibraries.length > 0) {
    selected = new Set(allLibraries)
  }

  function handleFilterChange(e: CustomEvent<{ selected: Set<string>; showUnchanged: boolean }>) {
    selected = e.detail.selected
    showUnchanged = e.detail.showUnchanged
  }

  $: visibleChanged = diff?.changed.filter(d => selected.has(d.group)) ?? []
  $: visibleUnchanged = showUnchanged
    ? (diff?.unchanged.filter(g => selected.has(g)) ?? [])
    : []
</script>

<header class="header">
  <div class="header-inner">
    <h1 class="site-title"><span class="brand">Compose</span> BOM Changelog</h1>
    <div class="controls">
      {#if fromBom && toBom}
        <BomSelector
          data={data.data}
          {fromBom}
          {toBom}
          on:change={handleSelectorChange}
        />
        <LibraryFilter
          libraries={allLibraries}
          {selected}
          {showUnchanged}
          on:change={handleFilterChange}
        />
      {/if}
    </div>
  </div>
</header>

<main class="main">
  <div class="container">
    {#if diff}
      {#if diff.whatsNew.length > 0}
        <section class="whats-new" aria-label="What's new articles">
          {#each diff.whatsNew as article}
            <WhatsNewCard {article} />
          {/each}
        </section>
      {/if}

      {#if visibleChanged.length > 0}
        <section class="changed" aria-label="Changed libraries">
          <div class="section-header">
            <h2 class="section-title">Changed</h2>
            <span class="count">{visibleChanged.length}</span>
          </div>
          <div class="library-list">
            {#each visibleChanged as libDiff (libDiff.group)}
              <LibraryDiff diff={libDiff} />
            {/each}
          </div>
        </section>
      {/if}

      {#if visibleUnchanged.length > 0}
        <section class="unchanged" aria-label="Unchanged libraries">
          <div class="section-header">
            <h2 class="section-title">Unchanged</h2>
            <span class="count">{visibleUnchanged.length}</span>
          </div>
          <div class="unchanged-list">
            {#each visibleUnchanged as group}
              <div class="unchanged-item">
                <span>{group.replace('androidx.', '')}</span>
                <span class="unchanged-version">
                  {data.data.bom_versions[toBom]?.libraries[group] ?? ''}
                </span>
              </div>
            {/each}
          </div>
        </section>
      {/if}

      {#if visibleChanged.length === 0 && !showUnchanged}
        <p class="empty">No changes to show. Use Filter to adjust what's visible.</p>
      {/if}
    {:else}
      <p class="empty">Loading…</p>
    {/if}
  </div>
</main>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--nav-bg);
    height: var(--header-height);
  }

  .header-inner {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 20px;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }

  .site-title {
    font-size: 17px;
    font-weight: 500;
    white-space: nowrap;
    color: #ffffff;
    letter-spacing: 0.01em;
  }

  .site-title .brand {
    color: var(--color-brand);
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    flex-wrap: wrap;
  }

  .main {
    padding: 24px 20px 48px;
  }

  .container {
    max-width: var(--max-width);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 28px;
  }

  .whats-new {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--color-border);
  }

  .section-title {
    font-size: 17px;
    font-weight: 600;
    color: var(--color-text);
  }

  .count {
    font-size: 13px;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 999px;
    padding: 1px 10px;
    color: var(--color-text-secondary);
    font-weight: 400;
  }

  .library-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .unchanged-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .unchanged-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-size: 13px;
  }

  .unchanged-version {
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    color: var(--color-text-secondary);
  }

  .empty {
    color: var(--color-text-secondary);
    font-size: 14px;
    text-align: center;
    padding: 40px 0;
  }

  @media (max-width: 600px) {
    .header {
      height: auto;
      padding: 12px 0;
    }

    .header-inner {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }

    .controls {
      width: 100%;
    }
  }
</style>
