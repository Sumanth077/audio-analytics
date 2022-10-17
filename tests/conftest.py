"""Pytest configuration and shared fixtures."""
import json
from typing import Any, Dict

import pytest
from steamship import Steamship

from tests import TEST_DATA

ENVIRONMENT = "cycle"
PACKAGE_HANDLE = "audio-analytics"


@pytest.fixture()
def config() -> Dict[str, Any]:
    """Load config from test data."""
    return json.load((TEST_DATA / "config.json").open())


@pytest.fixture()
def steamship_client() -> Steamship:
    """Get a Steamship client."""
    return Steamship(profile=ENVIRONMENT, workspace="test")
