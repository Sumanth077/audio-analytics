"""Test zendesk-ticket-urgency via integration tests."""

from steamship import App, AppInstance, Steamship

from tests.utils import load_audio, load_config

ENVIRONMENT = "prod"
APP_HANDLE = "audio-analytics-app"


def _get_app_instance():
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()
    app = App.get(client, handle=APP_HANDLE).data
    assert app is not None
    assert app.id is not None
    app_instance = AppInstance.create(client, app_id=app.id, config=config).data
    return app_instance


def test_transcribe():
    """Test label endpoint."""
    app_instance = _get_app_instance()
    audio = load_audio("test.mp3")

    response = app_instance.post("transcribe", audio=audio)
    assert response.data is not None
    assert response.data == "Mhm Mhm."
