# Zendesk Priority Classification

This project contains a Steamship App to summarize your audio files using Amazon Transcript and OneAI skills.

## Configuration

This plugin must be configured with the following fields:

| Parameter | Description | DType | Required |
|-------------------|----------------------------------------------------|--------|--|
| aws_access_key_id | AWS Access key that grants access to s3 and Amazon Transcribe | string |Yes|
| aws_secret_access_key | AWS Secret Access key that grans access to s3 and Amazon Transcribe | string |Yes|
| aws_s3_bucket_name | S3 bucket where the audio file and transcript will be stored. | string |Yes|
| aws_region | AWS Region where Amazon Transcribe will be invoked. | string |No|
| language_code | [Language identifier](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html) of
the dominant language spoken in the audio. | string |No|
| oneai_api_key | Your One AI API key. | string |Yes|
| oneai_skills | List of comma separated oneAI skills that produce tags. | string |Yes|
| oneai_input_type | Either `conversation` or `article`
. [One AI Documentation](https://studio.oneai.com/docs?api=Pipeline+API&item=Expected+Input+Format&accordion=Introduction%2CPipeline+API%2CNode.js+SDK+Reference%2CClustering+API)
| string |No|

## Usage

```python
from steamship import App, AppInstance, Steamship
from pathlib import Path
import base64

APP_HANDLE = 'audio-analytics-app'
PLUGIN_CONFIG = {
    "aws_access_key_id": "FILL_IN",
    "aws_secret_access_key": "FILL_IN",
    "aws_s3_bucket_name": "FILL_IN",
    "aws_region": "FILL_IN",
    "oneai_api_key": "FILL_IN",
    "oneai_skills": "FILL_IN",
    "oneai_input_type": "FILL_IN"
}
steamship = Steamship(profile="staging")  # Without arguments, credentials in ~/.steamship.json will be used.
# Fetch app definition
app = App.get(steamship, handle=APP_HANDLE).data
# Instantiate app
app_instance = AppInstance.create(
    steamship,
    app_id=app.id,
    config=PLUGIN_CONFIG,
).data
# Summarizing an audio file
with Path("AUDIO_FILE_PATH").open("rb") as f:
    audio = base64.b64encode(f.read()).decode("utf-8")
    app_instance.post("summarize", audio=audio)
```

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
