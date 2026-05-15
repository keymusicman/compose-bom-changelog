#!/usr/bin/env python3
"""Add a whats_new article entry for a BOM version to bom-data.json."""

import argparse
import json
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

DATA_FILE = Path(__file__).parent.parent / "data" / "bom-data.json"


def fetch_title(url: str) -> str:
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return url


def add_entry(data_file: Path, bom_version: str, url: str, summary: str, title: str) -> None:
    data = json.loads(data_file.read_text())
    article = {"title": title, "url": url, "summary": summary}
    if bom_version not in data["whats_new"]:
        data["whats_new"][bom_version] = []
    data["whats_new"][bom_version].append(article)
    data_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a whats_new entry for a BOM version.")
    parser.add_argument("bom_version", help="BOM version, e.g. 2026.05.00")
    parser.add_argument("page_url", help="URL of the release page or blog post")
    parser.add_argument("--summary", default="", help="Optional summary text")
    args = parser.parse_args()

    title = fetch_title(args.page_url)
    add_entry(DATA_FILE, args.bom_version, args.page_url, args.summary, title)
    print(f"Added '{title}' to whats_new[{args.bom_version}]")


if __name__ == "__main__":
    main()
