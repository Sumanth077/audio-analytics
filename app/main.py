import base64
import time
from copy import deepcopy
from pathlib import Path

import streamlit as st
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytube import YouTube
from steamship import Steamship, App, AppInstance, SteamshipError

APP_HANDLE = 'audio-analytics-app'
PLUGIN_CONFIG = {
    "aws_access_key_id": "AKIAYRUKYC4IP4SV2WFM",
    "aws_secret_access_key": "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",
    "aws_s3_bucket_name": "enias",
    "speaker_detection": True,
    "n_speakers": 2,
    "aws_region": "us-west-2",
    "oneai_api_key": "84ae4e01-e565-4791-a30c-181534f3eef4",
    "oneai_skills": "highlights,dialogue-segmentation",
    "oneai_input_type": "auto-detect"
}


@st.cache(allow_output_mutation=True)
def get_app_instance(n_speakers: int) -> AppInstance:
    steamship = Steamship(profile="prod")  # Without arguments, credentials in ~/.steamship.json will be used.

    config = deepcopy(PLUGIN_CONFIG)
    config["n_speakers"] = n_speakers

    # Fetch app definition
    app = App.get(steamship, handle=APP_HANDLE).data
    # Instantiate app
    return AppInstance.create(
        steamship,
        app_id=app.id,
        config=PLUGIN_CONFIG,
    ).data


def main():

    st.title("Podcast insights 👀")
    st.text(
        "Welcome to my first podcast analytics app! Using this app allows you to extract insights from your favorite podcasts.")

    youtube_url = st.text_input(label="Youtube url", placeholder="https://www.youtube.com/watch?v=-UX0X45sYe4")

    with st.expander("Expert settings"):
        n_speakers = st.number_input(label="Number of speakers", value=2)

    on_parse = st.button(label="Go!")
    if on_parse:
        st.video(youtube_url)

        with st.spinner(text="Downloading Youtube video..."):
            time.sleep(5)
            yt = YouTube(youtube_url)
            audio_stream_itag = yt.streams.filter(only_audio=True)[0].itag
            stream = yt.streams.get_by_itag(audio_stream_itag)
            video_file = stream.download()

        with st.spinner(text="Extracting audio track..."):
            clip = AudioFileClip(video_file)
            audio_file = video_file[:-4] + ".mp3"
            clip.write_audiofile(audio_file)
            clip.close()

        with st.spinner(text="Transcribing audio..."):
            app_instance = get_app_instance(n_speakers)
            with Path(audio_file).open("rb") as f:
                audio = base64.b64encode(f.read()).decode("utf-8")
                transcription = app_instance.post("transcribe", audio=audio, mime_type="audio/mp3")
            with st.expander("Transcription:"):
                try:
                    st.text(transcription.data)
                except SteamshipError as e:
                    st.error(f"Summarization failed : {e}")

        with st.spinner(text="Summarizing  audio..."):
            app_instance = get_app_instance(n_speakers)
            with Path(audio_file).open("rb") as f:
                audio = base64.b64encode(f.read()).decode("utf-8")
                insights = app_instance.post("summarize", audio=audio, mime_type="audio/mp3")
            try:
                st.write(insights.data)
            except SteamshipError as e:
                st.error(f"Summarization failed : {e}")
            st.subheader("Transcription:")
            st.text(insights)



if __name__ == '__main__':
    main()
