#!/usr/bin/env python3
"""
Compose BOM Changelog collector.

Fetches BOM version mappings from Google Maven and release notes
from AndroidX releases pages. Writes data/bom-data.json.
Additive only: never overwrites existing library_releases entries,
never touches the whats_new section.
"""

import html as html_module
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag

DATE_RE = re.compile(r"^[A-Z][a-z]+ \d{1,2}, \d{4}$")

DATA_FILE = Path(__file__).parent.parent / "data" / "bom-data.json"

MAVEN_BASE = "https://dl.google.com/android/maven2"
BOM_GROUP_PATH = "androidx/compose"
BOM_ARTIFACT = "compose-bom"

RELEASES_BASE = "https://developer.android.com/jetpack/androidx/releases"

MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}

ALLOWED_TAGS = {
    "p", "ul", "ol", "li", "h4", "h5", "strong", "b", "em",
    "code", "pre", "a", "br",
}
TAG_REMAP = {"b": "strong"}
VOID_TAGS = {"br"}


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
    if data["bom_versions"]:
        data["latest_bom_version"] = sorted(data["bom_versions"].keys())[-1]
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def maven_group_to_slug(group: str) -> str:
    """Convert Maven group ID to AndroidX releases page slug.

    androidx.compose.ui       -> compose-ui
    androidx.compose.material3 -> compose-material3
    androidx.activity         -> activity
    """
    return group.removeprefix("androidx.").replace(".", "-")


def _is_commits_paragraph(node: Tag) -> bool:
    if node.name != "p":
        return False
    for link in node.find_all("a"):
        if "commit" in link.get_text(strip=True).lower():
            return True
    return False


def _serialize(node: NavigableString | Tag) -> str:
    if isinstance(node, NavigableString):
        return html_module.escape(str(node), quote=False)

    if not hasattr(node, "name") or node.name is None:
        return ""

    name = node.name.lower()

    if name not in ALLOWED_TAGS:
        # drop the tag, keep its children
        return "".join(_serialize(c) for c in node.children)

    out_name = TAG_REMAP.get(name, name)

    if out_name in VOID_TAGS:
        return f"<{out_name}>"

    inner = "".join(_serialize(c) for c in node.children)

    if out_name == "a":
        href = node.get("href", "")
        return f'<a href="{html_module.escape(href)}" target="_blank" rel="noopener noreferrer">{inner}</a>'

    return f"<{out_name}>{inner}</{out_name}>"


def _is_date_only_paragraph(node: Tag) -> str:
    """Return the ISO date if this paragraph contains only a date like 'May 06, 2026'; '' otherwise."""
    if node.name != "p":
        return ""
    text = node.get_text(strip=True)
    if not DATE_RE.match(text):
        return ""
    try:
        return datetime.strptime(text, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


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


def scrape_release_notes(group: str, version: str) -> tuple[str, str, str]:
    """Scrape one version's release notes. Returns (html, commits_url, release_date)."""
    slug = maven_group_to_slug(group)
    url = f"{RELEASES_BASE}/{slug}"

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError:
        return "", "", ""

    soup = BeautifulSoup(resp.text, "lxml")

    version_id = version.replace(".", "_")
    heading = (
        soup.find(id=version)
        or soup.find(id=version_id)
        or soup.find(id=f"version_{version_id}")
        or soup.find(id=f"version-{version.replace('.', '-')}")
    )
    if not heading:
        return "", "", ""

    commits_url = _extract_commits_url(heading)

    parts: list[str] = []
    release_date = ""
    node = heading.next_sibling
    while node is not None:
        if hasattr(node, "name"):
            if node.name in ("h2", "h3"):
                break
            if isinstance(node, Tag):
                if _is_commits_paragraph(node):
                    node = node.next_sibling
                    continue
                if not release_date:
                    date = _is_date_only_paragraph(node)
                    if date:
                        release_date = date
                        node = node.next_sibling
                        continue
            parts.append(_serialize(node))
        node = node.next_sibling

    html = "".join(parts).strip()
    return html, commits_url, release_date


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
                release_notes_html, commits_url, scraped_date = scrape_release_notes(group, lib_version)
                release_date = scraped_date or get_release_date(group, lib_version)
                slug = maven_group_to_slug(group)
                release_notes_url = f"{RELEASES_BASE}/{slug}#{lib_version}"
                data["library_releases"][group][lib_version] = {
                    "release_date": release_date,
                    "release_notes_url": release_notes_url,
                    "commits_url": commits_url,
                    "release_notes_html": release_notes_html,
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
