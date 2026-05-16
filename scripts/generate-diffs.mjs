#!/usr/bin/env node
/**
 * Generates static JSON and Markdown diffs for adjacent BOM versions.
 * Output goes to site/static/diffs/ and is deployed alongside the site.
 *
 * Run: node scripts/generate-diffs.js
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')

const stripHtml = s => s.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()

const data = JSON.parse(readFileSync(join(root, 'data/bom-data.json'), 'utf8'))
const outDir = join(root, 'site/static/diffs')
mkdirSync(outDir, { recursive: true })

const sortedVersions = Object.keys(data.bom_versions).sort()

function compareSemver(a, b) {
  const parse = v => {
    const [main = '', pre = ''] = v.split('-')
    return { parts: main.split('.').map(Number), pre }
  }
  const av = parse(a), bv = parse(b)
  for (let i = 0; i < 3; i++) {
    const d = (av.parts[i] ?? 0) - (bv.parts[i] ?? 0)
    if (d !== 0) return d
  }
  if (!av.pre && bv.pre) return 1
  if (av.pre && !bv.pre) return -1
  return av.pre.localeCompare(bv.pre)
}

function computeDiff(fromBom, toBom) {
  const fromIdx = sortedVersions.indexOf(fromBom)
  const toIdx = sortedVersions.indexOf(toBom)
  const [actualFrom, actualTo, actualFromIdx, actualToIdx] =
    fromIdx <= toIdx
      ? [fromBom, toBom, fromIdx, toIdx]
      : [toBom, fromBom, toIdx, fromIdx]

  const fromLibs = data.bom_versions[actualFrom]?.libraries ?? {}
  const toLibs = data.bom_versions[actualTo]?.libraries ?? {}
  const allGroups = new Set([...Object.keys(fromLibs), ...Object.keys(toLibs)])

  const changed = []
  const unchanged = []

  for (const group of [...allGroups].sort()) {
    const fromVersion = fromLibs[group]
    const toVersion = toLibs[group]
    if (fromVersion === toVersion) {
      unchanged.push({ group, version: toVersion })
    } else {
      const groupReleases = data.library_releases[group] ?? {}
      const releases = fromVersion && toVersion
        ? Object.entries(groupReleases)
            .filter(([v]) => compareSemver(v, fromVersion) > 0 && compareSemver(v, toVersion) <= 0)
            .sort(([a], [b]) => compareSemver(a, b))
            .map(([version, r]) => ({ version, ...r }))
        : []
      changed.push({ group, fromVersion, toVersion, releases })
    }
  }

  const inRange = sortedVersions.slice(actualFromIdx + 1, actualToIdx + 1)
  const whatsNew = inRange.flatMap(v => data.whats_new?.[v] ?? [])

  return { from: actualFrom, to: actualTo, changed, unchanged, whatsNew }
}

function toMarkdown(diff) {
  const lines = []
  lines.push(`# Compose BOM Changelog: ${diff.from} → ${diff.to}`)
  lines.push('')
  lines.push(`Source: https://compose-bom.com/?from=${diff.from}&to=${diff.to}`)
  lines.push('')

  if (diff.whatsNew.length > 0) {
    lines.push('## What\'s New')
    for (const a of diff.whatsNew) {
      lines.push(`- [${a.title}](${a.url}) — ${a.summary}`)
    }
    lines.push('')
  }

  lines.push(`## Changed (${diff.changed.length})`)
  lines.push('')
  for (const lib of diff.changed) {
    const shortName = lib.group.replace('androidx.', '')
    lines.push(`### ${shortName}: ${lib.fromVersion ?? 'new'} → ${lib.toVersion ?? 'removed'}`)
    const allNew = lib.releases.flatMap(r => r.changes?.new_features ?? [])
    const allFixes = lib.releases.flatMap(r => r.changes?.bug_fixes ?? [])
    const allApi = lib.releases.flatMap(r => r.changes?.api_changes ?? [])
    if (allNew.length) { lines.push('**New Features**'); allNew.forEach(i => lines.push(`- ${stripHtml(i)}`)) }
    if (allFixes.length) { lines.push('**Bug Fixes**'); allFixes.forEach(i => lines.push(`- ${stripHtml(i)}`)) }
    if (allApi.length) { lines.push('**API Changes**'); allApi.forEach(i => lines.push(`- ${stripHtml(i)}`)) }
    if (!allNew.length && !allFixes.length && !allApi.length) lines.push('_No detailed release notes available._')
    const url = lib.releases.at(-1)?.release_notes_url
    if (url) lines.push(`Release notes: ${url}`)
    lines.push('')
  }

  if (diff.unchanged.length > 0) {
    lines.push(`## Unchanged (${diff.unchanged.length})`)
    lines.push('')
    for (const lib of diff.unchanged) {
      lines.push(`- ${lib.group.replace('androidx.', '')}: ${lib.version}`)
    }
  }

  return lines.join('\n')
}

// Generate diffs for each adjacent pair of BOM versions
const index = []
let count = 0
for (let i = 1; i < sortedVersions.length; i++) {
  const from = sortedVersions[i - 1]
  const to = sortedVersions[i]
  const slug = `${from}--${to}`
  const diff = computeDiff(from, to)

  writeFileSync(join(outDir, `${slug}.json`), JSON.stringify(diff, null, 2))
  writeFileSync(join(outDir, `${slug}.md`), toMarkdown(diff))

  index.push({
    from,
    to,
    changed: diff.changed.length,
    unchanged: diff.unchanged.length,
    json: `/diffs/${slug}.json`,
    md: `/diffs/${slug}.md`,
  })
  count++
}

writeFileSync(join(outDir, 'index.json'), JSON.stringify({ diffs: index }, null, 2))
console.log(`Generated ${count} diffs + index in site/static/diffs/`)
