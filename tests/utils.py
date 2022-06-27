"""Collection of utility function to support testing."""
import base64
import json
from typing import Any, Dict

from tests import TEST_DATA


def load_config() -> Dict[str, Any]:
    """Load config from test data."""
    return json.load((TEST_DATA / "config.json").open())


def load_audio(filename: str) -> str:
    """Load b64 encoded audio from test data."""
    audio_path = TEST_DATA / filename
    with audio_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
