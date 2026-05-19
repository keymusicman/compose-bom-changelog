<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import { goto } from '$app/navigation'
  import type { PageData } from './$types'
  import { computeDiff } from '$lib/diff'
  import { htmlToMarkdown } from '$lib/utils'
  import BomSelector from '$lib/components/BomSelector.svelte'
  import LibraryFilter from '$lib/components/LibraryFilter.svelte'
  import WhatsNewCard from '$lib/components/WhatsNewCard.svelte'
  import LibraryDiff from '$lib/components/LibraryDiff.svelte'
  import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte'

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

  let copiedAll = false
  let canShare = false

  onMount(() => { canShare = !!navigator.share })

  function buildAllText(): string {
    const header = `# Compose BOM: ${fromBom} → ${toBom}\n\nFull changelog: ${$page.url.href}`
    const sections = visibleChanged.map(d => {
      const from = d.fromVersion ?? 'new'
      const to = d.toVersion ?? 'removed'
      const lines: string[] = [`## ${d.group.replace('androidx.', '')}: ${from} → ${to}`]
      for (const r of d.releases) {
        const heading = r.release_date ? `${r.version} — ${r.release_date}` : r.version
        lines.push('', `### ${heading}`, '')
        lines.push(r.release_notes_html.trim() ? htmlToMarkdown(r.release_notes_html) : '_No changes_')
      }
      return lines.join('\n')
    })
    return [header, ...sections].join('\n\n')
  }

  function copyAllChanged() {
    navigator.clipboard.writeText(buildAllText())
    copiedAll = true
    setTimeout(() => { copiedAll = false }, 1500)
  }

  async function shareAllChanged() {
    await navigator.share({
      title: `Compose BOM: ${fromBom} → ${toBom}`,
      text: buildAllText(),
    })
  }
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
      <div class="controls-end">
        <ThemeSwitcher />
      </div>
    </div>
  </div>
</header>

<main class="main">
  <div class="container">
    {#if diff}
      {#if diff.whatsNew.length > 0}
        <section class="whats-new" aria-label="What's new articles">
          {#each diff.whatsNew as item}
            <WhatsNewCard article={item} bomVersion={item.bomVersion} />
          {/each}
        </section>
      {/if}

      {#if visibleChanged.length > 0}
        <section class="changed" aria-label="Changed libraries">
          <div class="section-header">
            <h2 class="section-title">Changed</h2>
            <span class="count">{visibleChanged.length}</span>
            <button class="copy-btn" class:done={copiedAll} on:click={copyAllChanged} title="Copy all" aria-label="Copy all changed libraries">
              {#if copiedAll}
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              {:else}
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                </svg>
              {/if}
            </button>
            {#if canShare}
              <button class="copy-btn share-btn" on:click={shareAllChanged} title="Share all" aria-label="Share all changed libraries">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                  <polyline points="16 6 12 2 8 6"/>
                  <line x1="12" y1="2" x2="12" y2="15"/>
                </svg>
              </button>
            {/if}
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
              {@const version = data.data.bom_versions[toBom]?.libraries[group] ?? ''}
              {@const releaseNotesUrl = version ? data.data.library_releases[group]?.[version]?.release_notes_url : undefined}
              <div class="unchanged-item">
                <span>{group.replace('androidx.', '')}</span>
                <div class="unchanged-right">
                  <span class="unchanged-version">{version}</span>
                  {#if releaseNotesUrl}
                    <a class="notes-link" href={releaseNotesUrl} target="_blank" rel="noopener noreferrer">Release notes ↗</a>
                  {/if}
                </div>
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

<footer class="footer">
  <a href="https://github.com/keymusicman/compose-bom-changelog" target="_blank" rel="noopener noreferrer" class="github-link">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.741 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
    </svg>
    View on GitHub
  </a>
</footer>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--nav-bg);
    border-bottom: 1px solid var(--nav-bottom-border);
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
    color: var(--nav-text);
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

  .controls-end {
    margin-left: auto;
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
    gap: 12px;
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

  .unchanged-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .unchanged-version {
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    color: var(--color-text-secondary);
  }

  .notes-link {
    font-size: 13px;
    color: var(--color-accent);
    white-space: nowrap;
  }

  .copy-btn {
    background: none;
    border: none;
    padding: 2px;
    color: var(--color-text-secondary);
    display: flex;
    align-items: center;
    opacity: 0.6;
    transition: opacity 0.15s, color 0.15s;
  }

  .copy-btn:hover {
    opacity: 1;
    color: var(--color-accent);
  }

  .copy-btn.done {
    color: var(--color-brand);
    opacity: 1;
  }

  .empty {
    color: var(--color-text-secondary);
    font-size: 14px;
    text-align: center;
    padding: 40px 0;
  }

  @media (hover: hover) and (pointer: fine) {
    .share-btn { display: none; }
  }

  .footer {
    text-align: center;
    padding: 24px 20px 32px;
    border-top: 1px solid var(--color-border);
  }

  .github-link {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 13px;
    color: var(--color-text-secondary);
    text-decoration: none;
    transition: color 0.15s;
  }

  .github-link:hover {
    color: var(--color-text);
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
      align-items: center;
    }

    .controls :global(.bom-selector) {
      width: 100%;
    }

    .controls :global(.filter-root) {
      margin-left: auto;
    }

    .controls-end {
      margin-left: 0;
    }
  }
</style>
