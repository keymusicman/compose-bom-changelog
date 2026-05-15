# Compose BOM Changelog

Browse diffs between any two [Jetpack Compose BOM](https://developer.android.com/jetpack/compose/bom) versions, with direct links to library release notes.

**[→ Open the site](https://keymusicman.github.io/compose-bom-changelog/)**

[![Latest BOM](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fkeymusicman.github.io%2Fcompose-bom-changelog%2Fdata%2Fbom-data.json&query=%24.latest_bom_version&label=latest%20BOM&color=blue)](https://keymusicman.github.io/compose-bom-changelog/)
[![Last updated](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fkeymusicman.github.io%2Fcompose-bom-changelog%2Fdata%2Fbom-data.json&query=%24.last_updated&label=last%20updated&color=green)](https://keymusicman.github.io/compose-bom-changelog/)

## How it works

A scheduled GitHub Actions job scrapes the Compose BOM release pages and commits updated library version data to `data/bom-data.json`. A SvelteKit static site reads that JSON and lets you select any two BOM versions to see what changed between them. Hosted on GitHub Pages — no backend.

## Local development

```bash
# Site
cp data/bom-data.json site/static/data/bom-data.json
cd site && npm run dev

# Collector
cd collector && source .venv/bin/activate
python collect.py
```
