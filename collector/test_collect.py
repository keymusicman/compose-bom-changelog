import pytest
from unittest.mock import patch, MagicMock
from collect import (
    find_versions_on_page,
    get_bom_libraries,
    get_bom_versions,
    maven_group_to_slug,
    scrape_release_notes,
)


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


METADATA_XML_WITH_EXCLUDED = """<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>androidx.compose</groupId>
  <artifactId>compose-bom</artifactId>
  <versioning>
    <versions>
      <version>2026.05.00</version>
      <version>2026.05.01</version>
      <version>2026.06.00</version>
    </versions>
  </versioning>
</metadata>"""


def test_get_bom_versions_skips_excluded():
    # 2026.05.01 was published to Maven but pulled from Google's official BOM
    # mapping (superseded by 2026.06.00). The immutable Maven artifact lingers,
    # so the collector must never re-add it.
    with patch("httpx.get", return_value=mock_response(METADATA_XML_WITH_EXCLUDED)):
        versions = get_bom_versions()
    assert versions == ["2026.05.00", "2026.06.00"]


RELEASES_HTML = """
<html><body>
  <h3 id="1.11.0">Version 1.11.0</h3>
  <p>April 2, 2026</p>
  <p>androidx.compose.ui:ui-*:1.11.0 is released. Version 1.11.0 contains <a href="https://googlesource.com/commits123">these commits</a>.</p>
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

RELEASES_HTML_RICH = """
<html><body>
  <h3 id="1.12.0">Version 1.12.0</h3>
  <p>May 1, 2026</p>
  <p>Version 1.12.0 contains <a href="https://googlesource.com/commits456">these commits</a>.</p>
  <h4>Bug Fixes</h4>
  <ul>
    <li><strong>State Reporting:</strong> Fixed isTransitionActive. (<a href="https://review.googlesource.com/d3426a">d3426a</a>, <a href="https://issuetracker.google.com/474385510">b/474385510</a>)</li>
    <li>Plain fix with no markup.</li>
  </ul>
</body></html>
"""

RELEASES_HTML_FREEFORM = """
<html><body>
  <h3 id="1.0.0-beta01">Version 1.0.0-beta01</h3>
  <p>April 7, 2021</p>
  <p>androidx.compose.animation:animation:1.0.0-beta01 is released. Version 1.0.0-beta01 contains <a href="https://googlesource.com/commitsAB">these commits</a>.</p>
  <p>Beta is a major milestone where all of the APIs and functionality are complete. <b>Compose 1.0 Beta</b> is ready for you to try out today.</p>
  <p>For more details on Compose 1.0 Beta, please see <a href="https://example.com/blog">our blog post</a>.</p>
  <h3 id="0.9.0">Version 0.9.0</h3>
</body></html>
"""

RELEASES_HTML_DISALLOWED = """
<html><body>
  <h3 id="2.0.0">Version 2.0.0</h3>
  <p>Date</p>
  <p>Version 2.0.0 contains <a href="https://googlesource.com/c">these commits</a>.</p>
  <div class="release-note-card">
    <p class="some-class">Wrapped content.</p>
    <script>alert('xss')</script>
    <ul>
      <li onclick="evil()">Item with handler</li>
    </ul>
  </div>
  <h3 id="1.0.0">Version 1.0.0</h3>
</body></html>
"""


def test_maven_group_to_slug():
    assert maven_group_to_slug("androidx.compose.ui") == "compose-ui"
    assert maven_group_to_slug("androidx.compose.material3") == "compose-material3"
    assert maven_group_to_slug("androidx.activity") == "activity"


def test_scrape_release_notes_returns_html_and_commits_and_date():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        html, commits_url, release_date = scrape_release_notes("androidx.compose.ui", "1.11.0")
    assert commits_url == "https://googlesource.com/commits123"
    assert release_date == "2026-04-02"
    assert "<h4>New Features</h4>" in html
    assert "<li>Added shared element debug tools</li>" in html
    assert "<li>Added trackpad event support</li>" in html
    assert "<h4>Bug Fixes</h4>" in html
    assert "<li>Fixed measurement issue</li>" in html


def test_scrape_release_notes_strips_commits_paragraph_and_date():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        html, _, _ = scrape_release_notes("androidx.compose.ui", "1.11.0")
    assert "these commits" not in html
    assert "is released" not in html
    assert "April 2, 2026" not in html


def test_scrape_release_notes_stops_at_next_version():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        html, _, _ = scrape_release_notes("androidx.compose.ui", "1.11.0")
    assert "1.10.0" not in html
    assert "February 1, 2026" not in html


def test_scrape_release_notes_returns_empty_on_missing_version():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML)):
        html, commits_url, release_date = scrape_release_notes("androidx.compose.ui", "9.9.9")
    assert html == ""
    assert commits_url == ""
    assert release_date == ""


def test_scrape_release_notes_preserves_bold_and_links():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML_RICH)):
        html, commits_url, release_date = scrape_release_notes("androidx.compose.ui", "1.12.0")
    assert commits_url == "https://googlesource.com/commits456"
    assert release_date == "2026-05-01"
    assert "<strong>State Reporting:</strong>" in html
    assert 'href="https://review.googlesource.com/d3426a"' in html
    assert ">d3426a<" in html
    assert 'href="https://issuetracker.google.com/474385510"' in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert "Plain fix with no markup." in html


def test_scrape_release_notes_captures_free_form_paragraphs():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML_FREEFORM)):
        html, commits_url, release_date = scrape_release_notes("androidx.compose.animation", "1.0.0-beta01")
    assert commits_url == "https://googlesource.com/commitsAB"
    assert release_date == "2021-04-07"
    assert "Beta is a major milestone" in html
    assert "<strong>Compose 1.0 Beta</strong>" in html
    assert 'href="https://example.com/blog"' in html
    assert "these commits" not in html
    assert "April 7, 2021" not in html


def test_scrape_release_notes_strips_disallowed_tags_and_attributes():
    with patch("httpx.get", return_value=mock_response(RELEASES_HTML_DISALLOWED)):
        html, _, _ = scrape_release_notes("androidx.compose.ui", "2.0.0")
    assert "<div" not in html
    assert "<script" not in html
    assert "release-note-card" not in html
    assert 'class="some-class"' not in html
    assert "onclick" not in html
    assert "Wrapped content." in html
    assert "<li>Item with handler</li>" in html


def test_scrape_release_notes_returns_empty_html_when_only_date():
    only_date_html = """
<html><body>
  <h3 id="3.0.0">Version 3.0.0</h3>
  <p>June 15, 2026</p>
  <p>Version 3.0.0 contains <a href="https://googlesource.com/x">these commits</a>.</p>
  <h3 id="2.9.0">Version 2.9.0</h3>
</body></html>
"""
    with patch("httpx.get", return_value=mock_response(only_date_html)):
        html, commits_url, release_date = scrape_release_notes("androidx.compose.ui", "3.0.0")
    assert html == ""
    assert release_date == "2026-06-15"
    assert commits_url == "https://googlesource.com/x"


VERSIONS_PAGE = """
<html><body>
  <h3 id="1.11.0">Version 1.11.0</h3>
  <h3 id="1.11.0-rc01">Version 1.11.0-rc01</h3>
  <h3 id="1.11.0-beta02">Version 1.11.0-beta02</h3>
  <h3 id="1.11.0-alpha05">Version 1.11.0-alpha05</h3>
  <h3 id="1.10.0">Version 1.10.0</h3>
  <h2 id="overview">Overview</h2>
  <h3 id="not-a-version">Some other anchor</h3>
  <h3 id="1.10">Not a full semver</h3>
</body></html>
"""


def test_find_versions_on_page_returns_only_semver_ids():
    versions = find_versions_on_page(VERSIONS_PAGE)
    assert set(versions) == {
        "1.11.0",
        "1.11.0-rc01",
        "1.11.0-beta02",
        "1.11.0-alpha05",
        "1.10.0",
    }


def test_scrape_release_notes_uses_provided_page_text():
    # When page_text is given, no HTTP call should happen
    with patch("httpx.get") as mock_get:
        html, commits_url, release_date = scrape_release_notes(
            "androidx.compose.ui", "1.11.0", page_text=RELEASES_HTML
        )
        assert not mock_get.called
    assert release_date == "2026-04-02"
    assert commits_url == "https://googlesource.com/commits123"
    assert "<li>Added shared element debug tools</li>" in html


def test_get_bom_libraries_groups_by_maven_group():
    with patch("httpx.get", return_value=mock_response(BOM_POM)):
        libraries = get_bom_libraries("2026.04.00")
    # The base artifact (ui) sets the group version; ui-graphics is ignored
    assert libraries == {
        "androidx.compose.ui": "1.11.0",
        "androidx.compose.material3": "1.4.0",
    }


BOM_POM_WITH_STRAGGLERS = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>androidx.compose.runtime</groupId>
        <artifactId>runtime</artifactId>
        <version>1.11.2</version>
      </dependency>
      <dependency>
        <groupId>androidx.compose.runtime</groupId>
        <artifactId>runtime-android</artifactId>
        <version>1.11.2</version>
      </dependency>
      <dependency>
        <groupId>androidx.compose.runtime</groupId>
        <artifactId>runtime-watchosx64</artifactId>
        <version>1.10.6</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>"""


def test_get_bom_libraries_uses_base_artifact_not_lagging_straggler():
    # Google sometimes leaves obscure KMP target artifacts (e.g. -watchosx64)
    # behind on an older version while the base artifact moves on. The group
    # version must follow the base artifact (runtime), not a lagging straggler.
    with patch("httpx.get", return_value=mock_response(BOM_POM_WITH_STRAGGLERS)):
        libraries = get_bom_libraries("2026.05.01")
    assert libraries == {"androidx.compose.runtime": "1.11.2"}
