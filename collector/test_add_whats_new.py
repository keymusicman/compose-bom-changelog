import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from add_whats_new import fetch_title, add_entry


def make_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_title_prefers_h1():
    html = "<html><head><title>Page Title</title></head><body><h1>Blog Post</h1></body></html>"
    with patch("add_whats_new.httpx.get", return_value=make_response(html)):
        assert fetch_title("https://example.com") == "Blog Post"


def test_fetch_title_falls_back_to_title_tag():
    html = "<html><head><title>Page Title</title></head><body></body></html>"
    with patch("add_whats_new.httpx.get", return_value=make_response(html)):
        assert fetch_title("https://example.com") == "Page Title"


def test_fetch_title_falls_back_to_url():
    html = "<html><body></body></html>"
    with patch("add_whats_new.httpx.get", return_value=make_response(html)):
        assert fetch_title("https://example.com") == "https://example.com"


def test_add_entry_creates_new_list(tmp_path: Path):
    data_file = tmp_path / "bom-data.json"
    data_file.write_text(json.dumps({
        "last_updated": "",
        "bom_versions": {},
        "library_releases": {},
        "whats_new": {},
    }))

    add_entry(data_file, "2026.05.00", "https://example.com/post", "Some summary", "Post Title")

    result = json.loads(data_file.read_text())
    assert result["whats_new"]["2026.05.00"] == [
        {"title": "Post Title", "url": "https://example.com/post", "summary": "Some summary"}
    ]


def test_add_entry_appends_to_existing_list(tmp_path: Path):
    data_file = tmp_path / "bom-data.json"
    data_file.write_text(json.dumps({
        "last_updated": "",
        "bom_versions": {},
        "library_releases": {},
        "whats_new": {
            "2026.05.00": [{"title": "First", "url": "https://a.com", "summary": ""}]
        },
    }))

    add_entry(data_file, "2026.05.00", "https://b.com", "", "Second")

    result = json.loads(data_file.read_text())
    assert len(result["whats_new"]["2026.05.00"]) == 2
    assert result["whats_new"]["2026.05.00"][1]["title"] == "Second"


def test_add_entry_empty_summary(tmp_path: Path):
    data_file = tmp_path / "bom-data.json"
    data_file.write_text(json.dumps({
        "last_updated": "", "bom_versions": {}, "library_releases": {}, "whats_new": {}
    }))

    add_entry(data_file, "2026.05.00", "https://example.com", "", "Title")

    result = json.loads(data_file.read_text())
    assert result["whats_new"]["2026.05.00"][0]["summary"] == ""
