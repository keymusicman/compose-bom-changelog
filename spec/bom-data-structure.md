# bom-data.json Structure Specification

Single source of truth for all data consumed by the static site.
Generated and maintained by the Python collector.

## Top-level shape

```json
{
  "last_updated": "<ISO 8601 timestamp>",
  "bom_versions": { ... },
  "library_releases": { ... },
  "whats_new": { ... }
}
```

---

## `bom_versions`

Keyed by BOM version string. Libraries are grouped by Maven group ID (not individual artifact),
since all artifacts within a group share the same version and release notes.

```json
"bom_versions": {
  "2026.05.00": {
    "release_date": "2026-05-01",
    "libraries": {
      "androidx.compose.ui": "1.11.1",
      "androidx.compose.material3": "1.4.1",
      "androidx.compose.runtime": "1.11.1",
      "androidx.compose.animation": "1.11.1",
      "androidx.compose.foundation": "1.11.1"
    }
  }
}
```

---

## `library_releases`

Keyed by Maven group ID, then by version string.
The collector populates this; commits can be added as a future extension without breaking changes.

```json
"library_releases": {
  "androidx.compose.ui": {
    "1.11.1": {
      "release_date": "2026-04-15",
      "release_notes_url": "https://developer.android.com/jetpack/androidx/releases/compose-ui#1.11.1",
      "changes": {
        "new_features": ["..."],
        "bug_fixes": ["..."],
        "api_changes": ["..."]
      }
    },
    "1.11.0": { ... }
  }
}
```

### Future extension: commits

A `commits` array can be added to any version entry without breaking existing consumers:

```json
"commits": [
  {
    "sha": "abc123",
    "message": "Fix layout issue in LazyColumn",
    "url": "https://github.com/androidx/androidx/commit/abc123"
  }
]
```

Source: AndroidX public GitHub mirror at `github.com/androidx/androidx`.

---

## `whats_new`

Keyed by BOM version string. Each entry is an array to support multiple articles per release.
This section is **hand-edited** — the collector never modifies it.

```json
"whats_new": {
  "2026.04.00": [
    {
      "title": "What's new in Jetpack Compose April '26",
      "url": "https://android-developers.googleblog.com/2026/04/jetpack-compose-april-2026-updates.html",
      "summary": "Shared element debug tools, trackpad events, and more."
    },
    {
      "title": "Compose Material 3 Adaptive 1.1 release",
      "url": "https://android-developers.googleblog.com/...",
      "summary": "..."
    }
  ]
}
```

---

## Collector responsibilities

- Scrapes `developer.android.com/develop/ui/compose/bom/bom-mapping` for BOM → library group version mappings
- Scrapes `developer.android.com/jetpack/androidx/releases/{library}` for release notes per version
- Parses changes into `new_features`, `bug_fixes`, `api_changes` sections
- Is **additive only**: never overwrites existing `library_releases` entries (version data is immutable once published)
- Never touches the `whats_new` section

## Key design decisions

- **Maven group, not artifact**: libraries are grouped by group ID (e.g., `androidx.compose.ui`)
  rather than individual artifact (e.g., `androidx.compose.ui:ui-graphics`) because all artifacts
  in a group share a version and release notes are written per group.
- **`whats_new` keyed by BOM version**: articles are associated with the BOM release they shipped with,
  and support multiple articles per BOM version.
- **Immutable version data**: once a library version's data is written, the collector does not re-scrape it,
  keeping the pipeline fast and the data stable.
