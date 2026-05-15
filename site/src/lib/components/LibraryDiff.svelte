<script lang="ts">
  import type { LibraryDiff as LibraryDiffType } from '$lib/diff'
  import ChangeSection from './ChangeSection.svelte'

  export let diff: LibraryDiffType

  $: hasChanges = diff.releases.some(r =>
    r.changes.new_features.length > 0 ||
    r.changes.bug_fixes.length > 0 ||
    r.changes.api_changes.length > 0
  )

  $: allNewFeatures = diff.releases.flatMap(r => r.changes.new_features)
  $: allBugFixes = diff.releases.flatMap(r => r.changes.bug_fixes)
  $: allApiChanges = diff.releases.flatMap(r => r.changes.api_changes)

  $: releaseNotesUrl = diff.releases.at(-1)?.release_notes_url
  $: commitsUrl = diff.releases.at(-1)?.commits_url

  let copied = false

  function stripHtml(html: string): string {
    return html.replace(/<[^>]+>/g, '')
  }

  function copy() {
    const from = diff.fromVersion ?? 'new'
    const to = diff.toVersion ?? 'removed'
    const lines: string[] = [`${diff.group.replace('androidx.', '')}: ${from} → ${to}`]
    if (allNewFeatures.length > 0) {
      lines.push('', 'New Features')
      allNewFeatures.forEach(f => lines.push(`· ${stripHtml(f)}`))
    }
    if (allBugFixes.length > 0) {
      lines.push('', 'Bug Fixes')
      allBugFixes.forEach(f => lines.push(`· ${stripHtml(f)}`))
    }
    if (allApiChanges.length > 0) {
      lines.push('', 'API Changes')
      allApiChanges.forEach(f => lines.push(`· ${stripHtml(f)}`))
    }
    navigator.clipboard.writeText(lines.join('\n'))
    copied = true
    setTimeout(() => { copied = false }, 1500)
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
    </div>
  </div>

  {#if hasChanges}
    <div class="body">
      <ChangeSection label="New Features" items={allNewFeatures} />
      <ChangeSection label="Bug Fixes" items={allBugFixes} />
      <ChangeSection label="API Changes" items={allApiChanges} />
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
    background: #fce8e6;
    color: #c5221f;
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

  @media (max-width: 600px) {
    .links {
      margin-left: 0;
    }
  }
</style>
