"""App that summarizes meetings using Amazon Transcribe and OneAI skills."""
import base64
from enum import Enum
from typing import Any, Dict, List

from steamship import File, PluginInstance, Steamship
from steamship.app import App, Response, create_handler, post
from steamship.plugin.config import Config

PRIORITY_LABEL = "priority"


class OneAIInputType(str, Enum):
    """Input types supported by OneAI."""

    ARTICLE = "article"
    CONVERSATION = "conversation"
    AUTO = "auto-detect"


class MeetingSummaryAppConfig(Config):
    """Config object containing required configuration parameters to initialize a MeetingSummaryApp."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket_name: str
    oneai_api_key: str
    oneai_skills: List[str]
    aws_region: str = "us-west-2"
    language_code: str = "en-US"
    oneai_input_type: OneAIInputType = OneAIInputType.AUTO

    def __init__(self, **kwargs):
        if isinstance(kwargs.get("oneai_skills"), str):
            kwargs["oneai_skills"] = kwargs["oneai_skills"].split(",")
        super().__init__(**kwargs)


class MeetingSummaryApp(App):
    """App that transcribes and summarizes audio using Amazon Transcribe and OneAI skills."""

    BLOCKIFIER_HANDLE = "amazon-s2t-blockifier"
    TAGGER_HANDLE = "oneai-tagger"

    def __init__(self, client: Steamship, config: Dict[str, Any]):
        super().__init__(client, config)
        self.config = MeetingSummaryAppConfig(**self.config)

        self.blockifier = PluginInstance.create(
            client,
            plugin_handle=self.BLOCKIFIER_HANDLE,
            config={
                "aws_access_key_id": self.config.aws_access_key_id,
                "aws_secret_access_key": self.config.aws_secret_access_key,
                "aws_s3_bucket_name": self.config.aws_s3_bucket_name,
                "aws_region": self.config.aws_region,
                "language_code": self.config.language_code,
            },
        ).data

        self.tagger = PluginInstance.create(
            client,
            plugin_handle=self.TAGGER_HANDLE,
            config={
                "api_key": self.config.oneai_api_key,
                "skills": ",".join(self.config.oneai_skills),
                "input_type": self.config.oneai_input_type,
            },
        ).data

    @post("transcribe")
    def transcribe(self, audio: str) -> Response:
        """Transcribe an audio file using Amazon Transcribe."""
        audio = base64.b64decode(audio.encode("utf-8"))
        file = File.create(self.client, content=audio, mime_type="audio/mp3").data
        file.blockify(plugin_instance=self.blockifier.handle).wait(
            max_timeout_s=300, retry_delay_s=30
        )
        file = file.refresh().data
        return Response(data=file.blocks[0].text)

    @post("summarize")
    def summarize(self, audio: str) -> Response:
        """Summarize audio using Amazon Transcribe and OneAI skills."""
        file = File.create(self.client, content=audio, mime_type="audio/mp3").data
        file.blockify(plugin_instance=self.blockifier.handle).wait(
            max_timeout_s=300, retry_delay_s=30
        )
        file.tag(plugin_instance=self.tagger.handle).wait()
        file = file.refresh().data
        return Response(data=[tag.dict() for block in file.blocks for tag in block.tags])


handler = create_handler(MeetingSummaryApp)
