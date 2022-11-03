"""Test audio-analytics package via integration test."""
from pathlib import Path
from test import INPUT_FILES
from test.conftest import PACKAGE_HANDLE
from test.utils import (
    TEST_URL,
    check_analyze_response,
    check_query_response,
    prep_workspace,
    upload_audio_file,
)
from typing import Any, Dict

import pytest
from steamship import File, PackageInstance, Steamship


@pytest.fixture()
def package_instance(config: Dict[str, Any], steamship_client: Steamship) -> PackageInstance:
    """Instantiate an instance of the audio-analytics package."""
    package_instance = steamship_client.use(package_handle=PACKAGE_HANDLE, config=config)
    assert package_instance is not None
    assert package_instance.id is not None
    return package_instance


def test_analyze_youtube(package_instance: PackageInstance) -> None:
    """Test the analyze_youtube endpoint."""
    response = package_instance.invoke("analyze_youtube", url=TEST_URL)
    check_analyze_response(package_instance, response)


@pytest.mark.parametrize("file", INPUT_FILES)
def test_analyze_url(
    steamship_client: Steamship, file: Path, package_instance: PackageInstance
) -> None:
    """Test the analyze_url endpoint."""
    mime_type = "audio/mp3" if "mp3" in file.suffix else "video/mp4"
    reading_signed_url = upload_audio_file(steamship_client, file, mime_type)

    response = package_instance.invoke("analyze_url", url=reading_signed_url)
    check_analyze_response(package_instance, response)


def test_query(steamship_client: Steamship, package_instance: PackageInstance) -> None:
    """Test the query endpoint."""
    prep_workspace(steamship_client)

    response = package_instance.invoke("query", query='filetag and kind "test_file"')
    check_query_response(response, File, "test_file", "file123")
