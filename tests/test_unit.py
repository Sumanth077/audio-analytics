"""Test zendesk-ticket-urgency via unit tests."""
from steamship import Steamship

from src.api import MeetingSummaryApp
from tests.utils import load_audio, load_config

ENVIRONMENT = "prod"


def test_transcribe() -> None:
    """Test label endpoint."""
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()
    audio = load_audio("test.mp3")
    app = MeetingSummaryApp(client, config=config)

    ret = app.transcribe(audio=audio)
    assert ret.data == "Mhm Mhm."


def test_summarize() -> None:
    """Test import endpoint."""
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()
    audio = load_audio("test.mp3")
    app = MeetingSummaryApp(client, config=config)

    ret = app.summarize(audio=audio)
    assert ret.data is not None
    assert isinstance(ret.data, list)
