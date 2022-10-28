"""Collection of helper functions for the jupyter notebooks."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from steamship import Steamship
from steamship.data.space import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url


def upload_audio_file(client: Steamship, filepath: Path, mime_type: str):
    """Upload a local file to the default workspace."""
    file_extension = mime_type.split("/")[1]
    unique_file_id = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid4()}.{file_extension}"
    writing_signed_url = (
        client.get_space()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.APP_DATA,
                filepath=unique_file_id,
                operation=SignedUrl.Operation.WRITE,
            )
        )
        .signed_url
    )
    upload_to_signed_url(writing_signed_url, filepath=filepath)
    reading_signed_url = (
        client.get_space()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.APP_DATA,
                filepath=unique_file_id,
                operation=SignedUrl.Operation.READ,
            )
        )
        .signed_url
    )
    return reading_signed_url
