#!/usr/bin/env python3
"""
One-off migration: replace the old `changes` field on every entry in
`data/bom-data.json` with a `release_notes_html` field produced by the
current scraper.

This is the only script allowed to overwrite existing `library_releases`
entries. The standard collector (`collect.py`) remains additive-only.

After this runs once and the result is committed, this script should
not need to be run again.
"""

import json
from pathlib import Path
from unittest.mock import patch

import httpx

from collect import (
    DATA_FILE,
    RELEASES_BASE,
    maven_group_to_slug,
    scrape_release_notes,
)


def fetch_library_page(group: str) -> str:
    slug = maven_group_to_slug(group)
    url = f"{RELEASES_BASE}/{slug}"
    print(f"  Fetching {url}")
    resp = httpx.get(url, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def main() -> None:
    data = json.loads(DATA_FILE.read_text())
    releases = data["library_releases"]

    libraries = sorted(releases.keys())
    print(f"Migrating {sum(len(v) for v in releases.values())} entries across {len(libraries)} libraries")

    pages: dict[str, str] = {}
    for group in libraries:
        pages[group] = fetch_library_page(group)

    total = 0
    populated = 0
    for group in libraries:
        page_html = pages[group]
        resp_stub = type("Resp", (), {
            "text": page_html,
            "status_code": 200,
            "raise_for_status": lambda self: None,
        })()

        # Reuse scrape_release_notes by patching httpx.get to return our cached page
        with patch("collect.httpx.get", return_value=resp_stub):
            versions = sorted(releases[group].keys())
            for version in versions:
                html, commits_url = scrape_release_notes(group, version)
                entry = releases[group][version]
                # Replace the old `changes` field with `release_notes_html`
                entry.pop("changes", None)
                entry["release_notes_html"] = html
                # Keep release_notes_url and release_date as they were.
                # commits_url: refresh only if we got one (the page is the source of truth);
                # don't blank out an existing value if the page didn't surface a link this time.
                if commits_url:
                    entry["commits_url"] = commits_url
                elif "commits_url" not in entry:
                    entry["commits_url"] = ""
                total += 1
                if html.strip():
                    populated += 1

    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Done. {populated}/{total} entries populated ({populated/total*100:.1f}%)")
    print(f"Empty: {total - populated} ({(total - populated)/total*100:.1f}%)")


if __name__ == "__main__":
    main()
