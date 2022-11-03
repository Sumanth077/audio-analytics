"""Test zendesk-ticket-urgency via unit test."""
from pathlib import Path
from typing import Any, Dict

import pytest
from steamship import File, Steamship

from src.api import AudioAnalyticsApp
from test import INPUT_FILES
from test.utils import (
    TEST_URL,
    check_analyze_response,
    check_query_response,
    prep_workspace,
    upload_audio_file,
)


@pytest.fixture()
def audio_analytics_app(config: Dict[str, Any], steamship_client: Steamship):
    """Instantiate an instance of AudioAnalyticsApp."""
    return AudioAnalyticsApp(client=steamship_client, config=config)


def test_analyze_youtube(audio_analytics_app: AudioAnalyticsApp) -> None:
    """Test the analyze_youtube endpoint."""
    response = audio_analytics_app.analyze_youtube(url=TEST_URL)
    check_analyze_response(audio_analytics_app, response)


@pytest.mark.parametrize("file", INPUT_FILES)
def test_analyze_url(
    steamship_client: Steamship, file: Path, audio_analytics_app: AudioAnalyticsApp
) -> None:
    """Test the analyze_url endpoint."""
    mime_type = "audio/mp3" if "mp3" in file.suffix else "video/mp4"

    reading_signed_url = upload_audio_file(steamship_client, file, mime_type)

    response = audio_analytics_app.analyze_url(url=reading_signed_url)
    check_analyze_response(audio_analytics_app, response)


def test_query(steamship_client: Steamship, audio_analytics_app: AudioAnalyticsApp) -> None:
    """Test the query endpoint."""
    prep_workspace(steamship_client)

    response = audio_analytics_app.query(query='filetag and kind "test_file"')

    check_query_response(response, File, "test_file", "file123")
