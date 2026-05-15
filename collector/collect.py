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
