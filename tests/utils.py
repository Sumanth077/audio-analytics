"""Collection of utility function to support testing."""
import base64
import json
import time
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Type, Union
from uuid import uuid4

from pydantic import parse_obj_as
from steamship import AppInstance, Block, File, Steamship, Tag
from steamship.app import Response
from steamship.base import TaskState
from steamship.data.space import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url

from src.api import AudioAnalyticsApp
from tests import TEST_DATA

TEST_URL = "https://www.youtube.com/watch?v=Nu0WXRXUfAk"


def check_analyze_response(app: Union[AudioAnalyticsApp, AppInstance], response):
    """Verify the response returned by the analyse endpoint."""
    assert response.data is not None
    assert "task_id" in response.data
    assert "status" in response.data
    assert response.data["status"] in (
        TaskState.succeeded,
        TaskState.failed,
        TaskState.running,
        TaskState.waiting,
    )

    task_id = response.data["task_id"]
    get_file = (
        app.get_file if isinstance(app, AudioAnalyticsApp) else partial(app.post, path="get_file")
    )
    response = get_file(task_id=task_id)
    n_retries = 0
    while n_retries <= 100 and response.data["status"] != TaskState.succeeded:
        response = get_file(task_id=task_id)
        time.sleep(2)

    assert response.data is not None
    assert "task_id" in response.data
    assert "status" in response.data
    assert response.data["status"] == TaskState.succeeded
    assert "file" in response.data
    file = response.data["file"]

    file = File.parse_obj(file) if not isinstance(file, File) else file
    assert file.blocks is not None
    assert len(file.blocks) > 0
    block = file.blocks[0]
    assert block.tags is not None
    assert len(block.tags) > 0


def load_config() -> Dict[str, Any]:
    """Load config from test data."""
    return json.load((TEST_DATA / "config.json").open())


def load_file(filename: Path) -> str:
    """Load b64 encoded audio from test data."""
    audio_path = TEST_DATA / "inputs" / filename
    with audio_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def upload_audio_file(file, mime_type):
    """Upload an audio file to the default workspace."""
    media_format = mime_type.split("/")[1]
    unique_file_id = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid4()}.{media_format}"
    s3_client = Steamship(profile="staging")
    writing_signed_url = (
        s3_client.get_space()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.APP_DATA,
                filepath=unique_file_id,
                operation=SignedUrl.Operation.WRITE,
            )
        )
        .data.signed_url
    )
    audio_path = TEST_DATA / "inputs" / file
    upload_to_signed_url(writing_signed_url, filepath=audio_path)
    reading_signed_url = (
        s3_client.get_space()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.APP_DATA,
                filepath=unique_file_id,
                operation=SignedUrl.Operation.READ,
            )
        )
        .data.signed_url
    )
    return reading_signed_url


def delete_files_in_space(client: Steamship) -> None:
    """Delete all files in the workspace."""
    for file in File.list(client).data.files:
        file.delete()


def check_query_response(
    response: Response, expected_type: Type[Union[File, Tag]], kind: str, name: str
) -> None:
    """Verify the response returned by the query endpoint."""
    assert response.data is not None
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    if not isinstance(response.data[0], expected_type):
        return_objects = parse_obj_as(List[expected_type], response.data)
    else:
        return_objects = response.data
    assert isinstance(return_objects[0], expected_type)
    tag = return_objects[0].tags[0] if expected_type is File else return_objects[0]
    assert tag.kind == kind
    assert tag.name == name


def prep_workspace(client: Steamship):
    """Prepare workspace by removing all files and adding a test file."""
    delete_files_in_space(client)
    File.create(
        client,
        tags=[Tag.CreateRequest(kind="test_file", name="file123")],
        blocks=[Block.CreateRequest(tags=[Tag.CreateRequest(kind="test_block", name="block123")])],
    )
