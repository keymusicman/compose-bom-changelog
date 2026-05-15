# Compose BOM Changelog

## Project overview

Static site that diffs two Jetpack Compose BOM versions and aggregates library release notes.
See `spec/` for full design and implementation plans.

## Repository structure

```
collector/     Python scraper (httpx + BeautifulSoup)
data/          bom-data.json — single source of truth, committed to repo
site/          SvelteKit static site (adapter-static)
spec/          Design docs and implementation plans
.github/       GitHub Actions workflows
```

## Commit discipline

- **Every commit must build.** Never commit broken code, even on feature branches.
- **Small, focused commits.** One logical change per commit. If a commit message needs "and", it should be two commits.
- **Commit often.** After each passing test, after each working component, after each config change.
- **Conventional commit prefixes:** `feat:`, `fix:`, `chore:`, `ci:`, `docs:`, `refactor:`, `test:`
- **No fixup commits** like "fix typo from last commit" — amend instead if not yet pushed.

## Development workflow

### Site (SvelteKit)

```bash
# Copy seed data before dev server
cp data/bom-data.json site/static/data/bom-data.json

cd site
npm run dev        # dev server at localhost:5173
npm run build      # build static site to site/build/
npm run check      # svelte-check type checking
npx vitest run     # run tests
```

### Collector (Python)

```bash
cd collector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python collect.py           # run collector (updates data/bom-data.json)
pytest test_collect.py -v   # run tests
```

## Code standards

- **Tests before implementation (TDD).** Write a failing test, then write the minimum code to make it pass.
- **Run tests before every commit.** A commit that skips tests is not a valid commit.
- **Type everything.** No `any` in TypeScript, no untyped Python functions.
- **No comments explaining what the code does** — only why, if the reason is non-obvious.
- **YAGNI.** Don't add features, abstractions, or error handling for scenarios not in the spec.
- **No useless tests.** Don't test framework behaviour, trivial getters, or implementation details. Test observable behaviour that would catch a real bug. A test that can never fail is worse than no test.

## Data integrity

- `data/bom-data.json` is the single source of truth.
- The collector is **additive only** — it never overwrites existing `library_releases` entries and never touches `whats_new`.
- `whats_new` is hand-edited. Never auto-generate or overwrite it.
- After running the collector, verify the JSON is valid before committing: `python -m json.tool data/bom-data.json > /dev/null`

## What not to do

- Don't run `git push --force` on `main`.
- Don't commit `site/static/data/bom-data.json` — it is copied at build time and should be in `.gitignore`.
- Don't add a UI component library — the UI is simple enough (two selects, one popover, cards) that plain CSS with the existing CSS variables is sufficient and keeps the bundle minimal.
- Don't add a backend or serverless functions — this is intentionally a static site.
