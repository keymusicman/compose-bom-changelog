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
