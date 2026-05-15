<script lang="ts">
  import type { Article } from '$lib/types'
  export let article: Article
</script>

<a class="card" href={article.url} target="_blank" rel="noopener noreferrer">
  <div class="icon" aria-hidden="true">🚀</div>
  <div class="content">
    <div class="title">{article.title}</div>
    <div class="summary">{article.summary}</div>
  </div>
  <svg class="chevron" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
    <path fill="currentColor" d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</a>

<style>
  .card {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
    background: var(--color-accent-light);
    border: 1px solid var(--color-accent);
    border-radius: var(--radius);
    color: var(--color-text);
    text-decoration: none;
    transition: box-shadow 0.15s;
  }

  .card:hover {
    box-shadow: var(--shadow);
    text-decoration: none;
  }

  .icon {
    font-size: 20px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .content {
    flex: 1;
    min-width: 0;
  }

  .title {
    font-weight: 600;
    font-size: 15px;
    color: var(--color-accent);
    margin-bottom: 2px;
  }

  .summary {
    font-size: 13px;
    color: var(--color-text-secondary);
    line-height: 1.4;
  }

  .chevron {
    color: var(--color-accent);
    flex-shrink: 0;
    margin-top: 3px;
  }
</style>
