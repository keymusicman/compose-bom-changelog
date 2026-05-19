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

from collect import (
    DATA_FILE,
    RELEASES_BASE,
    fetch_library_page,
    find_versions_on_page,
    maven_group_to_slug,
    scrape_release_notes,
)


def main() -> None:
    data = json.loads(DATA_FILE.read_text())
    releases = data["library_releases"]

    libraries = sorted(releases.keys())
    print(f"Starting with {sum(len(v) for v in releases.values())} entries across {len(libraries)} libraries")

    pages: dict[str, str] = {}
    for group in libraries:
        print(f"  Fetching {group}")
        pages[group] = fetch_library_page(group)

    # Per-group set of stable versions ever shipped in a BOM. We only keep
    # pre-releases (alpha/beta/rc) whose stable parent is in this set, otherwise
    # the dataset would grow with versions that no BOM diff would ever reach.
    bom_stables: dict[str, set[str]] = {}
    for bom_info in data["bom_versions"].values():
        for g, v in bom_info["libraries"].items():
            bom_stables.setdefault(g, set()).add(v)

    total = 0
    populated = 0
    added = 0
    for group in libraries:
        page_html = pages[group]
        slug = maven_group_to_slug(group)
        keep_stables = bom_stables.get(group, set())

        all_versions = find_versions_on_page(page_html)
        for v in all_versions:
            if "-" in v:
                stable_parent = v.split("-")[0]
                if stable_parent not in keep_stables:
                    continue
            if v not in releases[group]:
                releases[group][v] = {}
                added += 1

        for version in sorted(releases[group].keys()):
            entry = releases[group][version]
            html, commits_url, release_date = scrape_release_notes(group, version, page_text=page_html)
            entry.pop("changes", None)
            entry["release_notes_html"] = html
            entry["release_notes_url"] = f"{RELEASES_BASE}/{slug}#{version}"
            if release_date:
                entry["release_date"] = release_date
            elif "release_date" not in entry:
                entry["release_date"] = ""
            if commits_url:
                entry["commits_url"] = commits_url
            elif "commits_url" not in entry:
                entry["commits_url"] = ""
            total += 1
            if html.strip():
                populated += 1

    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Done. Added {added} pre-release entries.")
    print(f"{populated}/{total} entries populated ({populated/total*100:.1f}%)")
    print(f"Empty: {total - populated} ({(total - populated)/total*100:.1f}%)")


if __name__ == "__main__":
    main()
