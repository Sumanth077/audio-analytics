"""Test zendesk-ticket-urgency via unit tests."""
from pathlib import Path

import pytest
from steamship import File, Steamship, Tag

from src.api import AudioAnalyticsApp
from tests import INPUT_FILES
from tests.utils import (
    TEST_URL,
    check_analyze_response,
    check_query_response,
    load_config,
    prep_workspace,
    upload_audio_file,
)

ENVIRONMENT = "staging"


def test_analyze_youtube() -> None:
    """Test the analyze_youtube endpoint."""
    client = Steamship(profile=ENVIRONMENT, workspace="test")
    config = load_config()

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.analyze_youtube(url=TEST_URL)
    check_analyze_response(app, response)


@pytest.mark.parametrize("file", INPUT_FILES)
def test_analyze_url(file: Path) -> None:
    """Test the analyze_url endpoint."""
    client = Steamship(profile=ENVIRONMENT, workspace="test")
    config = load_config()
    mime_type = "audio/mp3" if "mp3" in file.suffix else "video/mp4"

    reading_signed_url = upload_audio_file(file, mime_type)

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.analyze_url(url=reading_signed_url)
    check_analyze_response(app, response)


def test_query_files() -> None:
    """Test the query_files endpoint."""
    client = Steamship(profile=ENVIRONMENT, workspace="test")
    config = load_config()

    prep_workspace(client)

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.query_files(query='filetag and kind "test_file"')

    check_query_response(response, File, "test_file", "file123")


def test_query_tags() -> None:
    """Test the query_tags endpoint."""
    client = Steamship(profile=ENVIRONMENT, workspace="test")
    config = load_config()

    prep_workspace(client)

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.query_tags(query='blocktag and kind "test_block"')

    check_query_response(response, Tag, "test_block", "block123")
