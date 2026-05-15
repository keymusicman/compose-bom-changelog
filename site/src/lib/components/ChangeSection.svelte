<script lang="ts">
  export let label: string
  export let items: string[]
</script>

{#if items.length > 0}
  <div class="section">
    <h4 class="section-label">{label}</h4>
    <ul class="items">
      {#each items as item}
        <li>{@html item}</li>
      {/each}
    </ul>
  </div>
{/if}

<style>
  .section {
    margin-top: 12px;
  }

  .section-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
    margin-bottom: 6px;
  }

  .items {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  li {
    font-size: 15px;
    line-height: 1.6;
    padding-left: 16px;
    position: relative;
    color: var(--color-text);
  }

  li::before {
    content: '·';
    position: absolute;
    left: 2px;
    color: var(--color-text-secondary);
    font-size: 18px;
    line-height: 1.3;
  }

  li :global(strong) {
    font-weight: 700;
  }

  li :global(a) {
    color: var(--color-accent);
    text-decoration: none;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.875em;
  }

  li :global(a:hover) {
    text-decoration: underline;
  }

  li :global(code) {
    font-family: 'Roboto Mono', 'Google Sans Mono', monospace;
    font-size: 0.85em;
    background: #f1f3f4;
    border: 1px solid #dadce0;
    padding: 2px 5px;
    border-radius: 4px;
    color: var(--color-text);
  }
</style>
