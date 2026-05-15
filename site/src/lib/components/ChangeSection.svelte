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
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-secondary);
    margin-bottom: 6px;
  }

  .items {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  li {
    font-size: 14px;
    line-height: 1.5;
    padding-left: 16px;
    position: relative;
  }

  li::before {
    content: '–';
    position: absolute;
    left: 0;
    color: var(--color-text-secondary);
  }
</style>
