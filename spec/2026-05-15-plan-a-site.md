# Compose BOM Changelog — Plan A: Site + CI/CD

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a static SvelteKit site that shows a diff between two Compose BOM versions, with aggregated release notes and "What's new" article cards.

**Architecture:** SvelteKit SPA with `adapter-static`; fetches `bom-data.json` at runtime from the static directory; all diff logic runs client-side; deployed to GitHub Pages via GitHub Actions on every push to `main`.

**Tech Stack:** SvelteKit 2, TypeScript, `@sveltejs/adapter-static`, Vitest, plain CSS (no UI library), GitHub Actions, GitHub Pages.

---

## File Map

```
compose-bom-changelog/
├── data/
│   └── bom-data.json              # seed file (hand-created in Task 1)
├── site/
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── static/
│   │   ├── CNAME                  # custom domain (set in Task 13)
│   │   └── data/
│   │       └── bom-data.json      # copied from data/ at build time
│   └── src/
│       ├── app.html
│       ├── app.css                # global styles + CSS variables
│       ├── routes/
│       │   ├── +layout.ts         # ssr=false, prerender=false
│       │   ├── +page.ts           # loads bom-data.json
│       │   └── +page.svelte       # root page
│       └── lib/
│           ├── types.ts
│           ├── diff.ts
│           ├── diff.test.ts
│           └── components/
│               ├── BomSelector.svelte
│               ├── LibraryFilter.svelte
│               ├── WhatsNewCard.svelte
│               ├── ChangeSection.svelte
│               └── LibraryDiff.svelte
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## Task 1: Project scaffold

**Files:**
- Create: `data/bom-data.json`
- Create: `site/` (SvelteKit project)
- Create: `site/svelte.config.js`
- Create: `site/vite.config.ts`

- [ ] **Step 1: Create seed bom-data.json**

```json
{
  "last_updated": "2026-05-15T00:00:00Z",
  "bom_versions": {
    "2026.04.00": {
      "release_date": "2026-04-02",
      "libraries": {
        "androidx.compose.ui": "1.11.0",
        "androidx.compose.material3": "1.4.0",
        "androidx.compose.runtime": "1.11.0",
        "androidx.compose.animation": "1.11.0",
        "androidx.compose.foundation": "1.11.0"
      }
    },
    "2026.05.00": {
      "release_date": "2026-05-07",
      "libraries": {
        "androidx.compose.ui": "1.11.1",
        "androidx.compose.material3": "1.4.1",
        "androidx.compose.runtime": "1.11.1",
        "androidx.compose.animation": "1.11.1",
        "androidx.compose.foundation": "1.11.0"
      }
    }
  },
  "library_releases": {
    "androidx.compose.ui": {
      "1.11.0": {
        "release_date": "2026-04-02",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-ui#1.11.0",
        "changes": {
          "new_features": ["Added shared element debug tools", "Added trackpad event support"],
          "bug_fixes": [],
          "api_changes": []
        }
      },
      "1.11.1": {
        "release_date": "2026-05-07",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-ui#1.11.1",
        "changes": {
          "new_features": [],
          "bug_fixes": ["Fixed layout measurement issue in LazyColumn"],
          "api_changes": []
        }
      }
    },
    "androidx.compose.material3": {
      "1.4.0": {
        "release_date": "2026-04-02",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-material3#1.4.0",
        "changes": {
          "new_features": ["Added ExpansionPanel component"],
          "bug_fixes": [],
          "api_changes": ["ExpansionPanel API is experimental"]
        }
      },
      "1.4.1": {
        "release_date": "2026-05-07",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-material3#1.4.1",
        "changes": {
          "new_features": [],
          "bug_fixes": ["Fixed ripple on NavigationBar"],
          "api_changes": []
        }
      }
    },
    "androidx.compose.runtime": {
      "1.11.0": {
        "release_date": "2026-04-02",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-runtime#1.11.0",
        "changes": {
          "new_features": [],
          "bug_fixes": ["Fixed recomposition loop edge case"],
          "api_changes": []
        }
      },
      "1.11.1": {
        "release_date": "2026-05-07",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-runtime#1.11.1",
        "changes": {
          "new_features": [],
          "bug_fixes": [],
          "api_changes": []
        }
      }
    },
    "androidx.compose.animation": {
      "1.11.0": {
        "release_date": "2026-04-02",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-animation#1.11.0",
        "changes": { "new_features": [], "bug_fixes": [], "api_changes": [] }
      },
      "1.11.1": {
        "release_date": "2026-05-07",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-animation#1.11.1",
        "changes": { "new_features": [], "bug_fixes": [], "api_changes": [] }
      }
    },
    "androidx.compose.foundation": {
      "1.11.0": {
        "release_date": "2026-04-02",
        "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-foundation#1.11.0",
        "changes": { "new_features": [], "bug_fixes": [], "api_changes": [] }
      }
    }
  },
  "whats_new": {
    "2026.04.00": [
      {
        "title": "What's new in Jetpack Compose April '26",
        "url": "https://android-developers.googleblog.com/2026/04/jetpack-compose-april-2026-updates.html",
        "summary": "Compose 1.11 brings shared element debug tools, trackpad event support, and more."
      }
    ]
  }
}
```

- [ ] **Step 2: Scaffold SvelteKit app**

Run from repo root:
```bash
npm create svelte@latest site
```
When prompted: Skeleton project, TypeScript, no ESLint, no Prettier, no Playwright, no Vitest (we add it manually).

- [ ] **Step 3: Install dependencies**

```bash
cd site
npm install
npm install -D @sveltejs/adapter-static vitest @vitest/ui jsdom @testing-library/svelte
```

- [ ] **Step 4: Configure adapter-static**

Replace contents of `site/svelte.config.js`:
```javascript
import adapter from '@sveltejs/adapter-static'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      fallback: '404.html'
    })
  }
}

export default config
```

- [ ] **Step 5: Configure Vite with Vitest**

Replace contents of `site/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import { sveltekit } from '@sveltejs/kit/vite'

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'jsdom',
    globals: true
  }
})
```

- [ ] **Step 6: Create static/data directory and copy seed data**

```bash
mkdir -p site/static/data
cp data/bom-data.json site/static/data/bom-data.json
```

- [ ] **Step 7: Commit**

```bash
git add data/bom-data.json site/
git commit -m "feat: scaffold SvelteKit site with adapter-static and seed data"
```

---

## Task 2: TypeScript types

**Files:**
- Create: `site/src/lib/types.ts`

- [ ] **Step 1: Write types.ts**

```typescript
export interface Changes {
  new_features: string[]
  bug_fixes: string[]
  api_changes: string[]
}

export interface Commit {
  sha: string
  message: string
  url: string
}

export interface LibraryVersion {
  release_date: string
  release_notes_url: string
  changes: Changes
  commits?: Commit[]
}

export interface BomVersion {
  release_date: string
  libraries: Record<string, string>  // maven_group -> version string
}

export interface Article {
  title: string
  url: string
  summary: string
}

export interface BomData {
  last_updated: string
  bom_versions: Record<string, BomVersion>
  library_releases: Record<string, Record<string, LibraryVersion>>
  whats_new: Record<string, Article[]>
}
```

- [ ] **Step 2: Commit**

```bash
git add site/src/lib/types.ts
git commit -m "feat: add TypeScript types for BOM data"
```

---

## Task 3: Diff logic (TDD)

**Files:**
- Create: `site/src/lib/diff.test.ts`
- Create: `site/src/lib/diff.ts`

- [ ] **Step 1: Write failing tests**

Create `site/src/lib/diff.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'
import { computeDiff } from './diff'
import type { BomData } from './types'

const testData: BomData = {
  last_updated: '2026-01-01T00:00:00Z',
  bom_versions: {
    '2026.01.00': {
      release_date: '2026-01-01',
      libraries: {
        'androidx.compose.ui': '1.10.0',
        'androidx.compose.material3': '1.3.0',
        'androidx.compose.runtime': '1.10.0',
      }
    },
    '2026.02.00': {
      release_date: '2026-02-01',
      libraries: {
        'androidx.compose.ui': '1.11.0',
        'androidx.compose.material3': '1.3.0',
        'androidx.compose.runtime': '1.11.0',
      }
    },
    '2026.03.00': {
      release_date: '2026-03-01',
      libraries: {
        'androidx.compose.ui': '1.11.1',
        'androidx.compose.material3': '1.4.0',
        'androidx.compose.runtime': '1.11.1',
      }
    },
  },
  library_releases: {
    'androidx.compose.ui': {
      '1.10.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/ui#1.10.0',
        changes: { new_features: [], bug_fixes: ['Fix A'], api_changes: [] }
      },
      '1.11.0': {
        release_date: '2026-02-01',
        release_notes_url: 'https://example.com/ui#1.11.0',
        changes: { new_features: ['Feature X'], bug_fixes: [], api_changes: [] }
      },
      '1.11.1': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/ui#1.11.1',
        changes: { new_features: [], bug_fixes: ['Fix B'], api_changes: [] }
      },
    },
    'androidx.compose.material3': {
      '1.3.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/material3#1.3.0',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
      '1.4.0': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/material3#1.4.0',
        changes: { new_features: ['Material Feature'], bug_fixes: [], api_changes: [] }
      },
    },
    'androidx.compose.runtime': {
      '1.10.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/runtime#1.10.0',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
      '1.11.0': {
        release_date: '2026-02-01',
        release_notes_url: 'https://example.com/runtime#1.11.0',
        changes: { new_features: [], bug_fixes: ['Runtime fix'], api_changes: [] }
      },
      '1.11.1': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/runtime#1.11.1',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
    },
  },
  whats_new: {
    '2026.02.00': [{ title: 'Feb release', url: 'https://example.com/feb', summary: 'New stuff' }],
    '2026.03.00': [{ title: 'Mar release', url: 'https://example.com/mar', summary: 'More stuff' }],
  }
}

describe('computeDiff', () => {
  it('identifies changed libraries', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.changed.map(c => c.group).sort()).toEqual([
      'androidx.compose.runtime',
      'androidx.compose.ui',
    ])
  })

  it('identifies unchanged libraries', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.unchanged).toEqual(['androidx.compose.material3'])
  })

  it('includes correct fromVersion and toVersion', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    const ui = result.changed.find(c => c.group === 'androidx.compose.ui')!
    expect(ui.fromVersion).toBe('1.10.0')
    expect(ui.toVersion).toBe('1.11.0')
  })

  it('includes all intermediate release notes in range', () => {
    const result = computeDiff('2026.01.00', '2026.03.00', testData)
    const ui = result.changed.find(c => c.group === 'androidx.compose.ui')!
    expect(ui.releases).toHaveLength(2) // 1.11.0 and 1.11.1, not 1.10.0
    expect(ui.releases[0].changes.new_features).toContain('Feature X')
    expect(ui.releases[1].changes.bug_fixes).toContain('Fix B')
  })

  it('collects whatsNew articles for BOM versions strictly after from, up to and including to', () => {
    const result = computeDiff('2026.01.00', '2026.03.00', testData)
    expect(result.whatsNew).toHaveLength(2)
    expect(result.whatsNew[0].title).toBe('Feb release')
    expect(result.whatsNew[1].title).toBe('Mar release')
  })

  it('does not include whatsNew for the fromBom itself', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.whatsNew).toHaveLength(1)
    expect(result.whatsNew[0].title).toBe('Feb release')
  })

  it('handles reversed from/to by swapping them', () => {
    const normal = computeDiff('2026.01.00', '2026.02.00', testData)
    const reversed = computeDiff('2026.02.00', '2026.01.00', testData)
    expect(reversed.changed.map(c => c.group).sort()).toEqual(
      normal.changed.map(c => c.group).sort()
    )
    expect(reversed.unchanged).toEqual(normal.unchanged)
  })
})
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd site && npx vitest run src/lib/diff.test.ts
```
Expected: FAIL — `Cannot find module './diff'`

- [ ] **Step 3: Implement diff.ts**

Create `site/src/lib/diff.ts`:
```typescript
import type { BomData, LibraryVersion, Article } from './types'

export interface LibraryDiff {
  group: string
  fromVersion: string | undefined
  toVersion: string | undefined
  releases: LibraryVersion[]
}

export interface DiffResult {
  changed: LibraryDiff[]
  unchanged: string[]
  whatsNew: Article[]
}

function parseSemver(v: string): [number, number, number, string] {
  const [main = '', pre = ''] = v.split('-')
  const [major = 0, minor = 0, patch = 0] = main.split('.').map(Number)
  return [major, minor, patch, pre]
}

function compareSemver(a: string, b: string): number {
  const [aMaj, aMin, aPatch, aPre] = parseSemver(a)
  const [bMaj, bMin, bPatch, bPre] = parseSemver(b)
  if (aMaj !== bMaj) return aMaj - bMaj
  if (aMin !== bMin) return aMin - bMin
  if (aPatch !== bPatch) return aPatch - bPatch
  // stable > pre-release
  if (!aPre && bPre) return 1
  if (aPre && !bPre) return -1
  return aPre.localeCompare(bPre)
}

function sortedBomVersions(data: BomData): string[] {
  // BOM versions are YYYY.MM.PP — lexicographic sort works due to zero-padding
  return Object.keys(data.bom_versions).sort()
}

function releasesInRange(
  groupReleases: Record<string, LibraryVersion>,
  fromVersion: string,
  toVersion: string
): LibraryVersion[] {
  return Object.entries(groupReleases)
    .filter(([v]) => compareSemver(v, fromVersion) > 0 && compareSemver(v, toVersion) <= 0)
    .sort(([a], [b]) => compareSemver(a, b))
    .map(([, release]) => release)
}

export function computeDiff(
  fromBom: string,
  toBom: string,
  data: BomData
): DiffResult {
  const sorted = sortedBomVersions(data)
  const fromIdx = sorted.indexOf(fromBom)
  const toIdx = sorted.indexOf(toBom)

  // Ensure from < to by swapping if reversed
  const [actualFrom, actualTo, actualFromIdx, actualToIdx] =
    fromIdx <= toIdx
      ? [fromBom, toBom, fromIdx, toIdx]
      : [toBom, fromBom, toIdx, fromIdx]

  const fromLibraries = data.bom_versions[actualFrom]?.libraries ?? {}
  const toLibraries = data.bom_versions[actualTo]?.libraries ?? {}
  const allGroups = new Set([...Object.keys(fromLibraries), ...Object.keys(toLibraries)])

  const changed: LibraryDiff[] = []
  const unchanged: string[] = []

  for (const group of [...allGroups].sort()) {
    const fromVersion = fromLibraries[group]
    const toVersion = toLibraries[group]

    if (fromVersion === toVersion) {
      unchanged.push(group)
    } else {
      const groupReleases = data.library_releases[group] ?? {}
      const releases =
        fromVersion && toVersion
          ? releasesInRange(groupReleases, fromVersion, toVersion)
          : []
      changed.push({ group, fromVersion, toVersion, releases })
    }
  }

  // whatsNew: BOM versions strictly after actualFrom, up to and including actualTo
  const inRange = sorted.slice(actualFromIdx + 1, actualToIdx + 1)
  const whatsNew = inRange.flatMap(v => data.whats_new[v] ?? [])

  return { changed, unchanged, whatsNew }
}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd site && npx vitest run src/lib/diff.test.ts
```
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/diff.ts site/src/lib/diff.test.ts
git commit -m "feat: implement BOM diff logic with tests"
```

---

## Task 4: App shell and data loading

**Files:**
- Modify: `site/src/app.html`
- Create: `site/src/app.css`
- Create: `site/src/routes/+layout.ts`
- Create: `site/src/routes/+page.ts`

- [ ] **Step 1: Update app.html**

Replace `site/src/app.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Compare Jetpack Compose BOM versions and see what changed" />
    <title>Compose BOM Changelog</title>
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    <div id="app">%sveltekit.body%</div>
  </body>
</html>
```

- [ ] **Step 2: Create app.css with CSS variables and base styles**

Create `site/src/app.css`:
```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --color-bg: #ffffff;
  --color-surface: #f8f9fa;
  --color-border: #e0e0e0;
  --color-text: #1a1a1a;
  --color-text-secondary: #6b7280;
  --color-accent: #4f46e5;
  --color-accent-light: #eef2ff;
  --color-added: #166534;
  --color-added-bg: #dcfce7;
  --color-changed: #92400e;
  --color-changed-bg: #fef3c7;
  --color-unchanged: #6b7280;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --max-width: 860px;
  --header-height: 64px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
}

a {
  color: var(--color-accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button {
  cursor: pointer;
  font: inherit;
}
```

- [ ] **Step 3: Create +layout.ts (disable SSR)**

Create `site/src/routes/+layout.ts`:
```typescript
export const ssr = false
export const prerender = false
```

- [ ] **Step 4: Create +page.ts (load BOM data)**

Create `site/src/routes/+page.ts`:
```typescript
import type { PageLoad } from './$types'
import type { BomData } from '$lib/types'

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch('/data/bom-data.json')
  if (!response.ok) {
    throw new Error(`Failed to load BOM data: ${response.status}`)
  }
  const data: BomData = await response.json()
  return { data }
}
```

- [ ] **Step 5: Import app.css in +layout.svelte**

If `site/src/routes/+layout.svelte` doesn't exist, create it:
```svelte
<script>
  import '../app.css'
</script>

<slot />
```

If it exists, add `import '../app.css'` inside the existing `<script>` block.

- [ ] **Step 6: Commit**

```bash
git add site/src/app.html site/src/app.css site/src/routes/
git commit -m "feat: add app shell, CSS variables, and data loading"
```

---

## Task 5: BomSelector component

**Files:**
- Create: `site/src/lib/components/BomSelector.svelte`

- [ ] **Step 1: Create BomSelector.svelte**

```svelte
<script lang="ts">
  import type { BomData } from '$lib/types'

  export let data: BomData
  export let fromBom: string
  export let toBom: string

  $: sortedVersions = Object.keys(data.bom_versions).sort().reverse()

  function handleFromChange(e: Event) {
    const value = (e.target as HTMLSelectElement).value
    dispatch('change', { fromBom: value, toBom })
  }

  function handleToChange(e: Event) {
    const value = (e.target as HTMLSelectElement).value
    dispatch('change', { fromBom, toBom: value })
  }

  import { createEventDispatcher } from 'svelte'
  const dispatch = createEventDispatcher<{ change: { fromBom: string; toBom: string } }>()
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
    gap: 8px;
    flex-wrap: wrap;
  }

  .selector-group {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .label {
    font-size: 14px;
    color: var(--color-text-secondary);
    white-space: nowrap;
  }

  select {
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 6px 28px 6px 10px;
    font-size: 14px;
    background: var(--color-bg);
    color: var(--color-text);
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
  }

  select:focus {
    outline: 2px solid var(--color-accent);
    outline-offset: 1px;
  }

  .arrow {
    color: var(--color-text-secondary);
    font-size: 16px;
  }

  @media (max-width: 480px) {
    .bom-selector {
      flex-direction: column;
      align-items: flex-start;
    }

    .arrow {
      transform: rotate(90deg);
    }

    select {
      width: 100%;
    }
  }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add site/src/lib/components/BomSelector.svelte
git commit -m "feat: add BomSelector component"
```

---

## Task 6: LibraryFilter component

**Files:**
- Create: `site/src/lib/components/LibraryFilter.svelte`

- [ ] **Step 1: Create LibraryFilter.svelte**

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let libraries: string[]        // all library groups in the diff
  export let selected: Set<string>      // which ones to show
  export let showUnchanged: boolean

  const dispatch = createEventDispatcher<{
    change: { selected: Set<string>; showUnchanged: boolean }
  }>()

  let open = false

  function toggleLibrary(group: string) {
    const next = new Set(selected)
    if (next.has(group)) {
      next.delete(group)
    } else {
      next.add(group)
    }
    dispatch('change', { selected: next, showUnchanged })
  }

  function toggleUnchanged() {
    dispatch('change', { selected, showUnchanged: !showUnchanged })
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false
  }

  function handleOutsideClick(e: MouseEvent) {
    const target = e.target as HTMLElement
    if (!target.closest('.filter-root')) open = false
  }

  $: activeCount = selected.size
  $: label = activeCount === libraries.length ? 'Filter' : `Filter (${activeCount}/${libraries.length})`
</script>

<svelte:window on:keydown={handleKeydown} on:click={handleOutsideClick} />

<div class="filter-root">
  <button
    class="filter-btn"
    class:active={activeCount !== libraries.length || showUnchanged}
    on:click|stopPropagation={() => (open = !open)}
    aria-expanded={open}
    aria-haspopup="listbox"
  >
    {label}
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
      <path fill="currentColor" d="M6 8L1 3h10z" />
    </svg>
  </button>

  {#if open}
    <div class="popover" role="listbox" aria-multiselectable="true">
      {#each libraries as group}
        <label class="option">
          <input
            type="checkbox"
            checked={selected.has(group)}
            on:change={() => toggleLibrary(group)}
          />
          <span>{group.replace('androidx.', '')}</span>
        </label>
      {/each}

      <div class="divider" />

      <label class="option">
        <input type="checkbox" checked={showUnchanged} on:change={toggleUnchanged} />
        <span>Show unchanged</span>
      </label>
    </div>
  {/if}
</div>

<style>
  .filter-root {
    position: relative;
  }

  .filter-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 6px 12px;
    font-size: 14px;
    background: var(--color-bg);
    color: var(--color-text);
    white-space: nowrap;
  }

  .filter-btn.active {
    border-color: var(--color-accent);
    color: var(--color-accent);
  }

  .popover {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    z-index: 100;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    min-width: 220px;
    padding: 8px 0;
  }

  .option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 16px;
    cursor: pointer;
    font-size: 14px;
  }

  .option:hover {
    background: var(--color-surface);
  }

  .option input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--color-accent);
    cursor: pointer;
    flex-shrink: 0;
  }

  .divider {
    height: 1px;
    background: var(--color-border);
    margin: 6px 0;
  }

  @media (max-width: 480px) {
    .popover {
      right: auto;
      left: 0;
      width: calc(100vw - 32px);
    }
  }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add site/src/lib/components/LibraryFilter.svelte
git commit -m "feat: add LibraryFilter popover component"
```

---

## Task 7: WhatsNewCard component

**Files:**
- Create: `site/src/lib/components/WhatsNewCard.svelte`

- [ ] **Step 1: Create WhatsNewCard.svelte**

```svelte
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
```

- [ ] **Step 2: Commit**

```bash
git add site/src/lib/components/WhatsNewCard.svelte
git commit -m "feat: add WhatsNewCard component"
```

---

## Task 8: ChangeSection and LibraryDiff components

**Files:**
- Create: `site/src/lib/components/ChangeSection.svelte`
- Create: `site/src/lib/components/LibraryDiff.svelte`

- [ ] **Step 1: Create ChangeSection.svelte**

```svelte
<script lang="ts">
  export let label: string
  export let items: string[]
</script>

{#if items.length > 0}
  <div class="section">
    <h4 class="section-label">{label}</h4>
    <ul class="items">
      {#each items as item}
        <li>{item}</li>
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
```

- [ ] **Step 2: Create LibraryDiff.svelte**

```svelte
<script lang="ts">
  import type { LibraryDiff as LibraryDiffType } from '$lib/diff'
  import ChangeSection from './ChangeSection.svelte'

  export let diff: LibraryDiffType

  $: hasChanges = diff.releases.some(r =>
    r.changes.new_features.length > 0 ||
    r.changes.bug_fixes.length > 0 ||
    r.changes.api_changes.length > 0
  )

  // Aggregate all changes across intermediate releases
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
```

- [ ] **Step 3: Commit**

```bash
git add site/src/lib/components/ChangeSection.svelte site/src/lib/components/LibraryDiff.svelte
git commit -m "feat: add ChangeSection and LibraryDiff components"
```

---

## Task 9: Main page composition

**Files:**
- Modify: `site/src/routes/+page.svelte`

- [ ] **Step 1: Write +page.svelte**

```svelte
<script lang="ts">
  import { page } from '$app/stores'
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'
  import type { PageData } from './$types'
  import { computeDiff } from '$lib/diff'
  import BomSelector from '$lib/components/BomSelector.svelte'
  import LibraryFilter from '$lib/components/LibraryFilter.svelte'
  import WhatsNewCard from '$lib/components/WhatsNewCard.svelte'
  import LibraryDiff from '$lib/components/LibraryDiff.svelte'

  export let data: PageData

  $: sortedVersions = Object.keys(data.data.bom_versions).sort()

  // Default: latest vs previous
  $: defaultTo = sortedVersions.at(-1) ?? ''
  $: defaultFrom = sortedVersions.at(-2) ?? ''

  let fromBom = ''
  let toBom = ''

  onMount(() => {
    fromBom = $page.url.searchParams.get('from') ?? defaultFrom
    toBom = $page.url.searchParams.get('to') ?? defaultTo
  })

  function handleSelectorChange(e: CustomEvent<{ fromBom: string; toBom: string }>) {
    fromBom = e.detail.fromBom
    toBom = e.detail.toBom
    const params = new URLSearchParams({ from: fromBom, to: toBom })
    goto(`?${params}`, { replaceState: false, keepFocus: true })
  }

  $: diff = fromBom && toBom ? computeDiff(fromBom, toBom, data.data) : null

  // Library filter state
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
    <h1 class="site-title">Compose BOM Changelog</h1>
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
    background: var(--color-bg);
    border-bottom: 1px solid var(--color-border);
    height: var(--header-height);
  }

  .header-inner {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 16px;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }

  .site-title {
    font-size: 16px;
    font-weight: 700;
    white-space: nowrap;
    color: var(--color-text);
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    flex-wrap: wrap;
  }

  .main {
    padding: 24px 16px;
  }

  .container {
    max-width: var(--max-width);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .whats-new {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 700;
  }

  .count {
    font-size: 13px;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 999px;
    padding: 1px 10px;
    color: var(--color-text-secondary);
  }

  .library-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .unchanged-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .unchanged-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--color-surface);
    border-radius: 6px;
    font-size: 14px;
  }

  .unchanged-version {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 13px;
    color: var(--color-text-secondary);
  }

  .empty {
    color: var(--color-text-secondary);
    font-size: 15px;
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
```

- [ ] **Step 2: Run the dev server and verify the page works**

```bash
cd site && npm run dev
```

Open `http://localhost:5173` in a browser. Verify:
- Two dropdowns show BOM versions
- Default selection is latest vs previous BOM
- Changed libraries show with version badges and release notes
- "What's new" card appears for the April '26 article
- Filter button opens popover with library checkboxes
- "Show unchanged" toggle works

- [ ] **Step 3: Commit**

```bash
git add site/src/routes/+page.svelte
git commit -m "feat: compose main page with diff view, filter, and what's new cards"
```

---

## Task 10: URL sync on page load

**Files:**
- Modify: `site/src/routes/+page.svelte`

- [ ] **Step 1: Subscribe to page store for URL changes**

The current `onMount` reads the URL once. Add a reactive statement to also react to `$page.url` changes (e.g., browser back/forward):

In the `<script>` block of `+page.svelte`, replace the `onMount` block with:

```typescript
  import { page } from '$app/stores'

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
```

Remove the `onMount` block entirely (the reactive statement handles initial load too).

- [ ] **Step 2: Verify URL sync**

With dev server running, manually navigate to `http://localhost:5173/?from=2026.04.00&to=2026.05.00`.
Verify the correct diff loads. Change a dropdown, verify the URL updates.

- [ ] **Step 3: Commit**

```bash
git add site/src/routes/+page.svelte
git commit -m "feat: sync BOM selection with URL query params bidirectionally"
```

---

## Task 11: GitHub Actions — deploy

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 1: Create deploy.yml**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: site/package-lock.json

      - name: Install dependencies
        run: cd site && npm ci

      - name: Copy BOM data into static directory
        run: cp data/bom-data.json site/static/data/bom-data.json

      - name: Build site
        run: cd site && npm run build

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site/build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Enable GitHub Pages in repository settings**

Go to the repository on GitHub → Settings → Pages → Source: GitHub Actions.

- [ ] **Step 3: Commit and push**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Pages deployment workflow"
git push origin main
```

- [ ] **Step 4: Verify deployment**

Open the Actions tab on GitHub and watch the deploy workflow. When it succeeds, open the published URL and verify the site loads and the diff works.

---

## Task 12: Custom domain (optional)

**Files:**
- Create: `site/static/CNAME`

- [ ] **Step 1: Create CNAME file**

```
# Replace with your actual domain
your-domain.com
```

- [ ] **Step 2: Configure DNS**

At your DNS provider, add a CNAME record pointing `your-domain.com` to `<your-github-username>.github.io`.

- [ ] **Step 3: Commit**

```bash
git add site/static/CNAME
git commit -m "chore: add custom domain CNAME"
git push origin main
```

---

## Self-Review

**Spec coverage check:**
- [x] Select two BOM versions — BomSelector + URL params
- [x] Aggregate release notes for every changed library — `computeDiff` + LibraryDiff
- [x] Select libraries to show — LibraryFilter with checkboxes
- [x] Show libraries that have not changed (hidden by default) — `showUnchanged` toggle, default false
- [x] Single page summarizing what changed — `+page.svelte`
- [x] "What's new" articles as callout cards — WhatsNewCard
- [x] Shareable URL — URL query params synced on every change
- [x] Default: latest vs previous BOM — `sortedVersions.at(-1)` and `.at(-2)`
- [x] Fully responsive — media queries in every component + header stacks on mobile

**Placeholder scan:** None found.

**Type consistency:**
- `LibraryDiff` defined in `diff.ts`, imported in `LibraryDiff.svelte` ✓
- `DiffResult.changed` is `LibraryDiff[]`, iterated in `+page.svelte` as `visibleChanged` ✓
- `BomData` defined in `types.ts`, used in `+page.ts` return and `+page.svelte` as `data.data` ✓
- `Article` used in `WhatsNewCard` matches `BomData.whats_new` shape ✓
