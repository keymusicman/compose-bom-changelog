<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import type { LibraryDiff as LibraryDiffType } from '$lib/diff'
  import { htmlToMarkdown } from '$lib/utils'

  export let diff: LibraryDiffType

  $: nonEmptyReleases = diff.releases.filter(r => r.release_notes_html.trim().length > 0)
  $: hasChanges = nonEmptyReleases.length > 0

  $: releaseNotesUrl = diff.releases.at(-1)?.release_notes_url
  $: commitsUrl = combinedCommitsUrl(diff.releases)

  function combinedCommitsUrl(releases: LibraryDiffType['releases']): string | undefined {
    if (releases.length === 0) return undefined
    const first = releases[0].commits_url
    const last = releases.at(-1)!.commits_url
    if (!first || !last) return last || first
    if (releases.length === 1) return last

    const logPattern = /\+log\/([a-f0-9]+)\.\.([a-f0-9]+)\/(.+)$/
    const firstMatch = first.match(logPattern)
    const lastMatch = last.match(logPattern)
    if (!firstMatch || !lastMatch) return last

    const base = last.slice(0, last.search(logPattern))
    return `${base}+log/${firstMatch[1]}..${lastMatch[2]}/${lastMatch[3]}`
  }

  let copied = false
  let canShare = false

  onMount(() => { canShare = !!navigator.share })

  function buildText(): string {
    const from = diff.fromVersion ?? 'new'
    const to = diff.toVersion ?? 'removed'
    const lines: string[] = [
      `# ${diff.group.replace('androidx.', '')}: ${from} → ${to}`,
      '',
      `Full changelog: ${$page.url.href}`,
    ]
    for (const r of nonEmptyReleases) {
      lines.push('', `## ${r.version}`)
      if (r.release_date) lines.push(`_${r.release_date}_`)
      lines.push('', htmlToMarkdown(r.release_notes_html))
    }
    return lines.join('\n')
  }

  function copy() {
    navigator.clipboard.writeText(buildText())
    copied = true
    setTimeout(() => { copied = false }, 1500)
  }

  async function share() {
    const from = diff.fromVersion ?? 'new'
    const to = diff.toVersion ?? 'removed'
    await navigator.share({
      title: `${diff.group.replace('androidx.', '')}: ${from} → ${to}`,
      text: buildText(),
    })
  }
</script>

<div class="card">
  <div class="header">
    <div class="group-name">{diff.group.replace('androidx.', '')}</div>
    <div class="version-badge">
      {#if diff.fromVersion}
        <span class="from">{diff.fromVersion}</span>
      {:else}
        <span class="added">new</span>
      {/if}
      <span class="arrow">→</span>
      {#if diff.toVersion}
        <span class="to">{diff.toVersion}</span>
      {:else}
        <span class="removed">removed</span>
      {/if}
    </div>
    <div class="links">
      {#if releaseNotesUrl}
        <a class="notes-link" href={releaseNotesUrl} target="_blank" rel="noopener noreferrer">
          Release notes ↗
        </a>
      {/if}
      {#if commitsUrl}
        <a class="notes-link" href={commitsUrl} target="_blank" rel="noopener noreferrer">
          All commits ↗
        </a>
      {/if}
      <button class="copy-btn" class:done={copied} on:click={copy} title="Copy" aria-label="Copy library info">
        {#if copied}
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
        <button class="copy-btn share-btn" on:click={share} title="Share" aria-label="Share library info">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
            <polyline points="16 6 12 2 8 6"/>
            <line x1="12" y1="2" x2="12" y2="15"/>
          </svg>
        </button>
      {/if}
    </div>
  </div>

  {#if hasChanges}
    <div class="body">
      {#each nonEmptyReleases as r (r.version)}
        <section class="release">
          <h4 class="release-version">
            <span class="version-num">{r.version}</span>
            {#if r.release_date}
              <span class="release-date">{r.release_date}</span>
            {/if}
          </h4>
          <div class="release-body">{@html r.release_notes_html}</div>
        </section>
      {/each}
    </div>
  {:else}
    <p class="no-changes">No detailed release notes available.</p>
  {/if}
</div>

<style>
  .card {
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    overflow: hidden;
    background: var(--color-bg);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s;
  }

  .card:hover {
    box-shadow: var(--shadow);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    padding: 12px 20px;
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
  }

  .group-name {
    font-weight: 700;
    font-size: 15px;
    color: var(--color-text);
  }

  .version-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-family: 'Roboto Mono', monospace;
  }

  .from {
    color: var(--color-text-secondary);
  }

  .arrow {
    color: var(--color-text-secondary);
    font-size: 11px;
  }

  .to {
    color: var(--color-accent);
    font-weight: 500;
  }

  .added {
    background: var(--color-added-bg);
    color: var(--color-added);
    padding: 1px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 500;
    font-family: inherit;
  }

  .removed {
    background: var(--color-removed-bg);
    color: var(--color-removed);
    padding: 1px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 500;
    font-family: inherit;
  }

  .links {
    margin-left: auto;
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .notes-link {
    font-size: 14px;
    color: var(--color-accent);
    white-space: nowrap;
  }

  .body {
    padding: 14px 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .release {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .release + .release {
    border-top: 1px dashed var(--color-border);
    padding-top: 14px;
  }

  .release-version {
    display: flex;
    align-items: baseline;
    gap: 10px;
    font-size: 13px;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .version-num {
    font-family: 'Roboto Mono', monospace;
    color: var(--color-text);
    font-weight: 600;
  }

  .release-date {
    font-size: 12px;
    color: var(--color-text-secondary);
  }

  .release-body {
    font-size: 15px;
    line-height: 1.6;
    color: var(--color-text);
  }

  .release-body :global(p) {
    margin: 0 0 8px;
  }

  .release-body :global(p:last-child) {
    margin-bottom: 0;
  }

  .release-body :global(h4),
  .release-body :global(h5) {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
    margin: 12px 0 6px;
  }

  .release-body :global(ul),
  .release-body :global(ol) {
    list-style: none;
    padding: 0;
    margin: 0 0 8px;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .release-body :global(li) {
    padding-left: 16px;
    position: relative;
  }

  .release-body :global(li::before) {
    content: '·';
    position: absolute;
    left: 2px;
    color: var(--color-text-secondary);
    font-size: 28px;
    line-height: 0.9;
  }

  .release-body :global(strong),
  .release-body :global(b) {
    font-weight: 700;
  }

  .release-body :global(em) {
    font-style: italic;
  }

  .release-body :global(a) {
    color: var(--color-accent);
    text-decoration: none;
  }

  .release-body :global(a:hover) {
    text-decoration: underline;
  }

  .release-body :global(code) {
    font-family: 'Roboto Mono', 'Google Sans Mono', monospace;
    font-size: 0.85em;
    background: var(--color-code-bg);
    border: 1px solid var(--color-border);
    padding: 2px 5px;
    border-radius: 4px;
    color: var(--color-text);
  }

  .release-body :global(pre) {
    background: var(--color-code-bg);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 10px 12px;
    overflow-x: auto;
    font-size: 13px;
  }

  .no-changes {
    padding: 12px 20px;
    font-size: 13px;
    color: var(--color-text-secondary);
    font-style: italic;
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

  @media (hover: hover) and (pointer: fine) {
    .share-btn { display: none; }
  }

  @media (max-width: 600px) {
    .links {
      margin-left: 0;
    }
  }
</style>
