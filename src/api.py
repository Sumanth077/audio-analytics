"""App that summarizes meetings using Amazon Transcribe and OneAI skills."""
import base64
import json
import pathlib
from enum import Enum
from typing import Optional, Type

import requests
import toml
from pydantic import HttpUrl
from steamship import File, MimeTypes, PluginInstance, Tag
from steamship.app import App, Response, create_handler, post
from steamship.base import Task, TaskState
from steamship.plugin.config import Config

PRIORITY_LABEL = "priority"


class OneAIInputType(str, Enum):
    """Input types supported by OneAI."""

    ARTICLE = "article"
    CONVERSATION = "conversation"
    AUTO = "auto-detect"


class AudioAnalyticsApp(App):
    """App that transcribes and summarizes audio using Amazon Transcribe and OneAI skills."""

    YOUTUBE_FILE_IMPORTER_HANDLE = "youtube-file-importer"
    ASSENBLYAI_BLOCKIFIER_HANDLE = "s2t-blockifier-default"

    class AudioAnalyticsAppConfig(Config):
        """Config object containing required configuration parameters to initialize a MeetingSummaryApp."""

        pass

    def config_cls(self) -> Type[Config]:
        """Return the Configuration class."""
        return self.AudioAnalyticsAppConfig

    def __init__(self, **kwargs):
        secret_kwargs = toml.load(
            str(pathlib.Path(__file__).parent / ".steamship" / "secrets.toml")
        )
        kwargs["config"] = {
            **secret_kwargs,
            **{k: v for k, v in kwargs["config"].items() if v != ""},
        }
        super().__init__(**kwargs)

        self.youtube_importer = PluginInstance.create(
            self.client,
            plugin_handle=self.YOUTUBE_FILE_IMPORTER_HANDLE,
            config={},
        ).data

        self.s2t_blockifier = PluginInstance.create(
            self.client,
            plugin_handle=self.ASSENBLYAI_BLOCKIFIER_HANDLE,
            config={},
        ).data

    @post("analyze_youtube")
    def analyze_youtube(self, url: HttpUrl) -> Response:
        """Summarize video from youtube using AssemblyAI."""
        file = File.create(self.client, plugin_instance=self.youtube_importer.handle, url=url).data
        return self._analyze_audio_file(file)

    @post("analyze_url")
    def analyze_url(self, url: HttpUrl, mime_type: Optional[MimeTypes] = None) -> Response:
        """Summarize audio from url using AssemblyAI."""
        mime_type = mime_type or MimeTypes.MP3
        file = File.create(self.client, content=requests.get(url).content, mime_type=mime_type).data
        return self._analyze_audio_file(file)

    @post("analyze")
    def analyze(self, audio: str, mime_type: str = MimeTypes.MP3) -> Response:
        """Summarize audio using AssemblyAI."""
        audio = base64.b64decode(audio.encode("utf-8"))
        file = File.create(self.client, content=audio, mime_type=mime_type).data
        return self._analyze_audio_file(file)

    @post("get_file")
    def get_file(self, task_id: str):
        """Get a file created by a task using the task ID."""
        task = Task.get(self.client, _id=task_id).data
        if task.state != TaskState.succeeded:
            return Response(json={"task_id": task.task_id, "status": task.state})
        else:
            file_id = json.loads(task.input)["id"]
            file = File.get(self.client, file_id).data
            return Response(json={"task_id": task.task_id, "status": task.state, "file": file.dict()})

    @post("query_files")
    def query_files(self, query: str) -> Response:
        """Query the files in the workspace."""
        return Response(json=File.query(self.client, query).data.files)

    @post("query_tags")
    def query_tags(self, query: str) -> Response:
        """Query the tags in the workspace."""
        return Response(json=Tag.query(self.client, query).data.tags)

    def _analyze_audio_file(self, file) -> Response:
        status = file.blockify(plugin_instance=self.s2t_blockifier.handle)
        task = status.task
        return Response(json={"task_id": task.task_id, "status": task.state})


handler = create_handler(AudioAnalyticsApp)
