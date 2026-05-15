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
from bs4 import BeautifulSoup, NavigableString, Tag

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


def maven_group_to_slug(group: str) -> str:
    """Convert Maven group ID to AndroidX releases page slug.

    androidx.compose.ui       -> compose-ui
    androidx.compose.material3 -> compose-material3
    androidx.activity         -> activity
    """
    return group.removeprefix("androidx.").replace(".", "-")


def _element_to_html(node: NavigableString | Tag) -> str:
    """Serialize a BS4 node to an HTML snippet, preserving safe inline tags."""
    if isinstance(node, NavigableString):
        return str(node)
    if node.name in ("strong", "b", "em"):
        inner = "".join(_element_to_html(c) for c in node.children)
        return f"<strong>{inner}</strong>"
    if node.name == "a":
        href = node.get("href", "")
        inner = "".join(_element_to_html(c) for c in node.children)
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{inner}</a>'
    if node.name == "code":
        inner = "".join(_element_to_html(c) for c in node.children)
        return f"<code>{inner}</code>"
    return "".join(_element_to_html(c) for c in node.children)


def _extract_commits_url(heading: Tag) -> str:
    """Return the googlesource 'these commits' URL from the paragraph after the heading."""
    node = heading.next_sibling
    while node is not None:
        if hasattr(node, "name"):
            if node.name in ("h2", "h3"):
                break
            if node.name == "p":
                link = node.find("a")
                if link and "commit" in link.get_text().lower():
                    return link.get("href", "")
        node = node.next_sibling
    return ""


def scrape_release_notes(
    group: str, version: str
) -> tuple[dict[str, list[str]], str]:
    slug = maven_group_to_slug(group)
    url = f"{RELEASES_BASE}/{slug}"
    empty: dict[str, list[str]] = {"new_features": [], "bug_fixes": [], "api_changes": []}

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError:
        return empty, ""

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
        return empty, ""

    commits_url = _extract_commits_url(heading)

    changes: dict[str, list[str]] = {"new_features": [], "bug_fixes": [], "api_changes": []}
    current_category: str | None = None
    node = heading.next_sibling

    while node is not None:
        if hasattr(node, "name"):
            if node.name in ("h2", "h3"):
                break
            if node.name in ("h4", "p"):
                label = node.get_text(strip=True).lower()
                current_category = next(
                    (v for k, v in CATEGORY_MAP.items() if k in label), None
                )
            elif node.name == "ul" and current_category:
                for li in node.find_all("li", recursive=False):
                    html = "".join(_element_to_html(c) for c in li.children).strip()
                    if html:
                        changes[current_category].append(html)
        node = node.next_sibling

    return changes, commits_url


def get_release_date(group: str, version: str) -> str:
    """Fetch release date from POM Last-Modified header, falling back to empty string."""
    slug = maven_group_to_slug(group)
    artifact = slug
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
            "release_date": "",
            "libraries": libraries,
        }

        for group, lib_version in libraries.items():
            if group not in data["library_releases"]:
                data["library_releases"][group] = {}

            if lib_version not in data["library_releases"][group]:
                print(f"    Scraping {group} {lib_version}…")
                changes, commits_url = scrape_release_notes(group, lib_version)
                release_date = get_release_date(group, lib_version)
                slug = maven_group_to_slug(group)
                release_notes_url = f"{RELEASES_BASE}/{slug}#{lib_version}"
                data["library_releases"][group][lib_version] = {
                    "release_date": release_date,
                    "release_notes_url": release_notes_url,
                    "commits_url": commits_url,
                    "changes": changes,
                }

    save(data)
    print(f"Done. Wrote {DATA_FILE}")


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


if __name__ == "__main__":
    main()
