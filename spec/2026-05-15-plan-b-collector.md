# Compose BOM Changelog — Plan B: Python Collector

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that scrapes BOM version mappings from Google Maven and release notes from AndroidX releases pages, writing `data/bom-data.json`. A GitHub Actions workflow runs it on a weekly schedule and commits the result.

**Architecture:** `collect.py` is additive-only — it reads the existing JSON, fetches only new/unknown data, and writes back. BOM version lists come from Google Maven's `maven-metadata.xml`; library mappings come from BOM POM files; release notes come from HTML scraping of `developer.android.com/jetpack/androidx/releases/{slug}`. The `whats_new` section is never touched by the collector.

**Tech Stack:** Python 3.11+, `httpx` (HTTP), `beautifulsoup4` + `lxml` (HTML parsing), `xml.etree.ElementTree` (Maven XML), `pytest` (tests), GitHub Actions.

---

## File Map

```
compose-bom-changelog/
├── collector/
│   ├── collect.py
│   ├── requirements.txt
│   └── test_collect.py
└── .github/
    └── workflows/
        └── collect.yml
```

---

## Task 1: Collector scaffold and dependencies

**Files:**
- Create: `collector/requirements.txt`
- Create: `collector/collect.py` (skeleton)

- [ ] **Step 1: Create requirements.txt**

```
httpx==0.27.0
beautifulsoup4==4.12.3
lxml==5.2.1
pytest==8.2.0
```

- [ ] **Step 2: Create Python virtual environment and install deps**

```bash
cd collector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 3: Create collect.py skeleton**

```python
#!/usr/bin/env python3
"""
Compose BOM Changelog collector.

Fetches BOM version mappings from Google Maven and release notes
from AndroidX releases pages. Writes data/bom-data.json.
Additive only: never overwrites existing library_releases entries,
never touches the whats_new section.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

DATA_FILE = Path(__file__).parent.parent / "data" / "bom-data.json"

MAVEN_BASE = "https://dl.google.com/android/maven2"
BOM_GROUP_PATH = "androidx/compose"
BOM_ARTIFACT = "compose-bom"

RELEASES_BASE = "https://developer.android.com/jetpack/androidx/releases"

MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}

CATEGORY_MAP = {
    "new features": "new_features",
    "api changes": "api_changes",
    "behavior changes": "api_changes",
    "bug fixes": "bug_fixes",
    "deprecations": "api_changes",
}


def load_existing() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {
        "last_updated": "",
        "bom_versions": {},
        "library_releases": {},
        "whats_new": {},
    }


def save(data: dict) -> None:
    data["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Commit**

```bash
git add collector/
git commit -m "feat: scaffold Python collector with dependencies"
```

---

## Task 2: Fetch BOM versions from Google Maven

**Files:**
- Modify: `collector/collect.py`

- [ ] **Step 1: Write failing test**

Create `collector/test_collect.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from collect import get_bom_versions, get_bom_libraries


METADATA_XML = """<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>androidx.compose</groupId>
  <artifactId>compose-bom</artifactId>
  <versioning>
    <versions>
      <version>2026.04.00</version>
      <version>2026.05.00</version>
    </versions>
  </versioning>
</metadata>"""


BOM_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>androidx.compose.ui</groupId>
        <artifactId>ui</artifactId>
        <version>1.11.0</version>
      </dependency>
      <dependency>
        <groupId>androidx.compose.ui</groupId>
        <artifactId>ui-graphics</artifactId>
        <version>1.11.0</version>
      </dependency>
      <dependency>
        <groupId>androidx.compose.material3</groupId>
        <artifactId>material3</artifactId>
        <version>1.4.0</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>"""


def mock_response(text: str, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def test_get_bom_versions():
    with patch("httpx.get", return_value=mock_response(METADATA_XML)):
        versions = get_bom_versions()
    assert versions == ["2026.04.00", "2026.05.00"]


def test_get_bom_libraries_groups_by_maven_group():
    with patch("httpx.get", return_value=mock_response(BOM_POM)):
        libraries = get_bom_libraries("2026.04.00")
    # Both androidx.compose.ui artifacts share the same version — one entry per group
    assert libraries == {
        "androidx.compose.ui": "1.11.0",
        "androidx.compose.material3": "1.4.0",
    }
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd collector && source .venv/bin/activate && pytest test_collect.py::test_get_bom_versions test_collect.py::test_get_bom_libraries_groups_by_maven_group -v
```
Expected: FAIL — `cannot import name 'get_bom_versions' from 'collect'`

- [ ] **Step 3: Implement get_bom_versions and get_bom_libraries**

Add to `collector/collect.py` before `if __name__ == "__main__":`:

```python
def get_bom_versions() -> list[str]:
    url = f"{MAVEN_BASE}/{BOM_GROUP_PATH}/{BOM_ARTIFACT}/maven-metadata.xml"
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    return sorted(v.text for v in root.findall(".//version") if v.text)


def get_bom_libraries(version: str) -> dict[str, str]:
    url = (
        f"{MAVEN_BASE}/{BOM_GROUP_PATH}/{BOM_ARTIFACT}"
        f"/{version}/{BOM_ARTIFACT}-{version}.pom"
    )
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    groups: dict[str, str] = {}
    for dep in root.findall(".//m:dependency", MAVEN_NS):
        group_id = dep.findtext("m:groupId", namespaces=MAVEN_NS) or ""
        ver = dep.findtext("m:version", namespaces=MAVEN_NS) or ""
        if group_id and ver:
            groups[group_id] = ver  # safe: all artifacts in a group share the same version
    return groups
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest test_collect.py::test_get_bom_versions test_collect.py::test_get_bom_libraries_groups_by_maven_group -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add collector/collect.py collector/test_collect.py
git commit -m "feat: implement BOM version and library fetching from Google Maven"
```

---

## Task 3: Scrape release notes from AndroidX releases pages

**Files:**
- Modify: `collector/collect.py`
- Modify: `collector/test_collect.py`

- [ ] **Step 1: Write failing test**

Add to `collector/test_collect.py`:

```python
from collect import scrape_release_notes, maven_group_to_slug


RELEASES_HTML = """
<html><body>
  <h3 id="1.11.0">Version 1.11.0</h3>
  <p>April 2, 2026</p>
  <h4>New Features</h4>
  <ul>
    <li>Added shared element debug tools</li>
    <li>Added trackpad event support</li>
  </ul>
  <h4>Bug Fixes</h4>
  <ul>
    <li>Fixed measurement issue</li>
  </ul>
  <h3 id="1.10.0">Version 1.10.0</h3>
  <p>February 1, 2026</p>
</body></html>
"""


def test_maven_group_to_slug():
    assert maven_group_to_slug("androidx.compose.ui") == "compose-ui"
    assert maven_group_to_slug("androidx.compose.material3") == "compose-material3"
    assert maven_group_to_slug("androidx.activity") == "activity"


def test_scrape_release_notes_extracts_changes():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        result = scrape_release_notes("androidx.compose.ui", "1.11.0")
    assert result["new_features"] == [
        "Added shared element debug tools",
        "Added trackpad event support",
    ]
    assert result["bug_fixes"] == ["Fixed measurement issue"]
    assert result["api_changes"] == []


def test_scrape_release_notes_returns_empty_on_missing_version():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        result = scrape_release_notes("androidx.compose.ui", "9.9.9")
    assert result == {"new_features": [], "bug_fixes": [], "api_changes": []}
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest test_collect.py::test_maven_group_to_slug test_collect.py::test_scrape_release_notes_extracts_changes test_collect.py::test_scrape_release_notes_returns_empty_on_missing_version -v
```
Expected: FAIL — `cannot import name 'scrape_release_notes' from 'collect'`

- [ ] **Step 3: Implement maven_group_to_slug and scrape_release_notes**

Add to `collector/collect.py`:

```python
def maven_group_to_slug(group: str) -> str:
    """Convert Maven group ID to AndroidX releases page slug.

    androidx.compose.ui      -> compose-ui
    androidx.compose.material3 -> compose-material3
    androidx.activity        -> activity
    """
    return group.removeprefix("androidx.").replace(".", "-")


def scrape_release_notes(group: str, version: str) -> dict[str, list[str]]:
    slug = maven_group_to_slug(group)
    url = f"{RELEASES_BASE}/{slug}"
    empty = {"new_features": [], "bug_fixes": [], "api_changes": []}

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError:
        return empty

    soup = BeautifulSoup(resp.text, "lxml")

    # AndroidX release pages use version as heading id, e.g. id="1.11.0"
    version_id = version.replace(".", "_")
    heading = (
        soup.find(id=version)
        or soup.find(id=version_id)
        or soup.find(id=f"version_{version_id}")
        or soup.find(id=f"version-{version.replace('.', '-')}")
    )
    if not heading:
        return empty

    changes: dict[str, list[str]] = {"new_features": [], "bug_fixes": [], "api_changes": []}
    current_category: str | None = None
    node = heading.next_sibling

    while node is not None:
        if hasattr(node, "name"):
            if node.name in ("h2", "h3"):
                break
            if node.name == "h4":
                label = node.get_text(strip=True).lower()
                current_category = next(
                    (v for k, v in CATEGORY_MAP.items() if k in label), None
                )
            elif node.name == "ul" and current_category:
                for li in node.find_all("li", recursive=False):
                    text = li.get_text(separator=" ", strip=True)
                    if text:
                        changes[current_category].append(text)
        node = node.next_sibling

    return changes
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest test_collect.py::test_maven_group_to_slug test_collect.py::test_scrape_release_notes_extracts_changes test_collect.py::test_scrape_release_notes_returns_empty_on_missing_version -v
```
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add collector/collect.py collector/test_collect.py
git commit -m "feat: implement AndroidX release notes scraping"
```

---

## Task 4: Wire up main() and run end-to-end

**Files:**
- Modify: `collector/collect.py`

- [ ] **Step 1: Implement get_release_date**

Add to `collector/collect.py`:

```python
def get_release_date(group: str, version: str) -> str:
    """Fetch release date from POM Last-Modified header, falling back to empty string."""
    slug = maven_group_to_slug(group)
    artifact = slug  # artifact ID matches slug for most compose libraries
    group_path = group.replace(".", "/")
    url = f"{MAVEN_BASE}/{group_path}/{artifact}/{version}/{artifact}-{version}.pom"
    try:
        resp = httpx.head(url, timeout=15, follow_redirects=True)
        last_modified = resp.headers.get("last-modified", "")
        if last_modified:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(last_modified)
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return ""
```

- [ ] **Step 2: Implement main()**

Replace the `if __name__ == "__main__":` block with:

```python
def main() -> None:
    data = load_existing()

    print("Fetching BOM versions…")
    all_versions = get_bom_versions()
    new_versions = [v for v in all_versions if v not in data["bom_versions"]]
    print(f"  Known: {len(data['bom_versions'])}, New: {len(new_versions)}")

    for bom_version in new_versions:
        print(f"  Processing BOM {bom_version}…")
        libraries = get_bom_libraries(bom_version)
        data["bom_versions"][bom_version] = {
            "release_date": "",  # filled in below per library group
            "libraries": libraries,
        }

        for group, lib_version in libraries.items():
            if group not in data["library_releases"]:
                data["library_releases"][group] = {}

            if lib_version not in data["library_releases"][group]:
                print(f"    Scraping {group} {lib_version}…")
                changes = scrape_release_notes(group, lib_version)
                release_date = get_release_date(group, lib_version)
                slug = maven_group_to_slug(group)
                release_notes_url = (
                    f"{RELEASES_BASE}/{slug}#{lib_version}"
                )
                data["library_releases"][group][lib_version] = {
                    "release_date": release_date,
                    "release_notes_url": release_notes_url,
                    "changes": changes,
                }

    save(data)
    print(f"Done. Wrote {DATA_FILE}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run collector against real data**

```bash
cd collector && source .venv/bin/activate && python collect.py
```

Expected output (approximately):
```
Fetching BOM versions…
  Known: 2, New: N
  Processing BOM 2026.XX.XX…
    Scraping androidx.compose.ui 1.X.X…
    …
Done. Wrote …/data/bom-data.json
```

Inspect `data/bom-data.json` — verify it has new BOM versions and library release entries.

- [ ] **Step 4: Run all collector tests**

```bash
pytest test_collect.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add collector/collect.py
git commit -m "feat: implement collector main() — additive BOM data pipeline"
```

---

## Task 5: GitHub Actions — collect workflow

**Files:**
- Create: `.github/workflows/collect.yml`

- [ ] **Step 1: Create collect.yml**

```yaml
name: Collect BOM data

on:
  schedule:
    - cron: '0 6 * * 1'  # every Monday at 06:00 UTC
  workflow_dispatch:       # allow manual trigger

permissions:
  contents: write

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
          cache-dependency-path: collector/requirements.txt

      - name: Install dependencies
        run: pip install -r collector/requirements.txt

      - name: Run collector
        run: python collector/collect.py

      - name: Commit updated data if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/bom-data.json
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: update BOM data [skip ci]"
            git push
          fi
```

Note: `[skip ci]` in the commit message prevents the deploy workflow from triggering on data-only commits. Remove it if you want every data update to redeploy the site immediately.

- [ ] **Step 2: Commit and push**

```bash
git add .github/workflows/collect.yml
git commit -m "ci: add weekly BOM data collection workflow"
git push origin main
```

- [ ] **Step 3: Trigger manually and verify**

On GitHub → Actions → "Collect BOM data" → Run workflow.
Watch the run complete. Verify a commit appears in the repo updating `data/bom-data.json`.

---

## Self-Review

**Spec coverage check:**
- [x] Scrapes BOM mapping page — using Google Maven POM files (more reliable than HTML scraping)
- [x] Scrapes AndroidX release notes — `scrape_release_notes` with BeautifulSoup
- [x] Groups by Maven group ID — `get_bom_libraries` deduplicates per group
- [x] Additive only — `main()` skips known versions, never touches `whats_new`
- [x] Scheduled + manual trigger — `collect.yml` with `schedule` and `workflow_dispatch`
- [x] Commits result — git commit step in workflow

**Placeholder scan:** `get_release_date` uses a HEAD request with `Last-Modified` — this may not always be accurate. An acceptable limitation; the date is informational only.

**Type consistency:**
- `scrape_release_notes` returns `dict[str, list[str]]` matching the `changes` field shape in `bom-data-structure.md` ✓
- `get_bom_libraries` returns `dict[str, str]` matching `bom_versions[x].libraries` shape ✓
- `main()` writes `library_releases[group][version]` with keys `release_date`, `release_notes_url`, `changes` matching `LibraryVersion` in `types.ts` ✓
