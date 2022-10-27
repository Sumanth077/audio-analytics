"""Package that transcribes, analyses, and indexes audio and video."""
import json
from typing import List, Optional, Type

import requests
from pydantic import HttpUrl
from steamship import File, MimeTypes, Tag
from steamship.base import Task, TaskState
from steamship.invocable import Config, Invocable, InvocableResponse, create_handler, post

PRIORITY_LABEL = "priority"


class AudioAnalyticsApp(Invocable):
    """Package that transcribes and summarizes audio."""

    YOUTUBE_FILE_IMPORTER_HANDLE = "youtube-file-importer"
    S2T_BLOCKIFIER_HANDLE = "s2t-blockifier-default"

    class AudioAnalyticsAppConfig(Config):
        """Config object containing required configuration parameters to initialize a AudioAnalyticsApp."""

        pass

    def config_cls(self) -> Type[Config]:
        """Return the Configuration class."""
        return self.AudioAnalyticsAppConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.youtube_importer = self.client.use_plugin(
            plugin_handle=self.YOUTUBE_FILE_IMPORTER_HANDLE
        )
        self.s2t_blockifier = self.client.use_plugin(plugin_handle=self.S2T_BLOCKIFIER_HANDLE)

    class FileTag:
        """Simplified File tag representation."""

        kind: str
        name: str

    @post("analyze_youtube")
    def analyze_youtube(self, url: HttpUrl) -> InvocableResponse:
        """Transcribe and analyze a Youtube video."""
        file_create_task = File.create_with_plugin(
            self.client, plugin_instance=self.youtube_importer.handle, url=url
        )
        file_create_task.wait(max_timeout_s=5 * 60)  # Wait for 5 minutes
        file = file_create_task.output
        return self._analyze_audio_file(file)

    @post("analyze_url")
    def analyze_url(
        self,
        url: HttpUrl,
        mime_type: Optional[MimeTypes] = None,
        tags: Optional[List[FileTag]] = None,
    ) -> InvocableResponse:
        """Transcribe and analyze audio from a publicly available URL."""
        mime_type = mime_type or MimeTypes.MP3
        file = File.create(self.client, content=requests.get(url).content, mime_type=mime_type)
        for tag in tags or []:
            Tag.create(self.client, file.id, kind=tag["kind"], name=tag["name"])
        return self._analyze_audio_file(file)

    @post("status")
    def get_status(self, task_id: str):
        """Get a file created by a task using the task ID."""
        task = Task.get(self.client, _id=task_id)
        if task.state != TaskState.succeeded:
            return InvocableResponse(json={"task_id": task.task_id, "status": task.state})
        else:
            file_id = json.loads(task.input)["id"]
            file = File.get(self.client, file_id)
            return InvocableResponse(
                json={"task_id": task.task_id, "status": task.state, "file": file.dict()}
            )

    @post("query")
    def query(self, query: str) -> InvocableResponse:
        """Query the files in the workspace."""
        return InvocableResponse(json=File.query(self.client, tag_filter_query=query).files)

    def _analyze_audio_file(self, file) -> InvocableResponse:
        blockify_task = file.blockify(plugin_instance=self.s2t_blockifier.handle)
        return InvocableResponse(
            json={"task_id": blockify_task.task_id, "status": blockify_task.state}
        )


handler = create_handler(AudioAnalyticsApp)
