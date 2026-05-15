import pytest
from unittest.mock import patch, MagicMock
from collect import get_bom_versions, get_bom_libraries, scrape_release_notes, maven_group_to_slug


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


RELEASES_HTML = """
<html><body>
  <h3 id="1.11.0">Version 1.11.0</h3>
  <p>April 2, 2026</p>
  <p>New Features</p>
  <ul>
    <li>Added shared element debug tools</li>
    <li>Added trackpad event support</li>
  </ul>
  <p>Bug Fixes</p>
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


def test_get_bom_libraries_groups_by_maven_group():
    with patch("httpx.get", return_value=mock_response(BOM_POM)):
        libraries = get_bom_libraries("2026.04.00")
    # Both androidx.compose.ui artifacts share the same version — one entry per group
    assert libraries == {
        "androidx.compose.ui": "1.11.0",
        "androidx.compose.material3": "1.4.0",
    }
