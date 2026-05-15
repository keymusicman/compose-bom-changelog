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
    {#if releaseNotesUrl}
      <a class="notes-link" href={releaseNotesUrl} target="_blank" rel="noopener noreferrer">
        Release notes ↗
      </a>
    {/if}
  </div>

  {#if hasChanges}
    <div class="changes">
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
    padding: 16px;
    background: var(--color-bg);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .group-name {
    font-weight: 600;
    font-size: 15px;
  }

  .version-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-family: 'SF Mono', 'Fira Code', monospace;
  }

  .from {
    color: var(--color-text-secondary);
  }

  .arrow {
    color: var(--color-text-secondary);
  }

  .to {
    color: var(--color-accent);
    font-weight: 600;
  }

  .added {
    background: var(--color-added-bg);
    color: var(--color-added);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
  }

  .removed {
    background: #fef2f2;
    color: #991b1b;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
  }

  .notes-link {
    margin-left: auto;
    font-size: 13px;
    color: var(--color-accent);
    white-space: nowrap;
  }

  .changes {
    margin-top: 4px;
  }

  .no-changes {
    margin-top: 10px;
    font-size: 14px;
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
