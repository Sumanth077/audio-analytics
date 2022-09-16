"""Test zendesk-ticket-urgency via unit tests."""
from pathlib import Path

import pytest
from steamship import Steamship

from src.api import AudioAnalyticsApp
from tests import INPUT_FILES
from tests.utils import load_config, TEST_URL, check_analyze_response, upload_audio_file

ENVIRONMENT = "staging"


def test_analyze_youtube() -> None:
    """Test import endpoint."""
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.analyze_youtube(url=TEST_URL)
    check_analyze_response(app, response)


@pytest.mark.parametrize("file", INPUT_FILES)
def test_analyze_url(file: Path) -> None:
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()
    mime_type = "audio/mp3" if "mp3" in file.suffix else "video/mp4"

    reading_signed_url = upload_audio_file(file, mime_type)

    app = AudioAnalyticsApp(client=client, config=config)
    response = app.analyze_url(url=reading_signed_url)
    check_analyze_response(app, response)
