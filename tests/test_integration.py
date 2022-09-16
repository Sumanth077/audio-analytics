"""Test zendesk-ticket-urgency via integration tests."""
from pathlib import Path

import pytest
from steamship import AppInstance, Steamship, MimeTypes

from tests import INPUT_FILES
from tests.utils import load_file, load_config, check_analyze_response, TEST_URL, upload_audio_file

ENVIRONMENT = "staging"
APP_HANDLE = "audio-analytics-app"


def _get_app_instance():
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()
    app_instance = AppInstance.create(client, app_handle=APP_HANDLE, config=config).data
    assert app_instance is not None
    assert app_instance.id is not None
    return app_instance

def test_analyze_youtube() -> None:
    """Test import endpoint."""
    app_instance = _get_app_instance()

    response = app_instance.post("analyze_youtube", url=TEST_URL)
    check_analyze_response(app_instance, response)


@pytest.mark.parametrize("file", INPUT_FILES)
def test_analyze_url(file: Path) -> None:
    app_instance = _get_app_instance()
    mime_type = "audio/mp3" if "mp3" in file.suffix else "video/mp4"
    reading_signed_url = upload_audio_file(file, mime_type)

    response = app_instance.post("analyze_url", url=reading_signed_url)
    check_analyze_response(app_instance, response)
