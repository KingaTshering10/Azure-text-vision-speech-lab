"""Shared configuration and Azure helpers. Importing this module makes no API calls."""

import base64
from dataclasses import dataclass, field
import mimetypes
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AzureSettings:
    endpoint: str
    key: str = field(repr=False)
    deployment: str
    api_version: str

    @classmethod
    def load(cls, service="text"):
        prefixes = {"text": "AZURE_OAI", "asr": "AZURE_ASR", "tts": "AZURE_TTS"}
        versions = {"text": "2024-10-21", "asr": "2024-10-21", "tts": "2025-03-01-preview"}
        if service not in prefixes:
            raise ValueError("service must be text, asr, or tts")
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
        prefix = prefixes[service]
        values = [os.getenv(f"{prefix}_{name}", "").strip()
                  for name in ("ENDPOINT", "KEY", "DEPLOYMENT")]
        missing = [f"{prefix}_{name}" for name, value in
                   zip(("ENDPOINT", "KEY", "DEPLOYMENT"), values)
                   if not value or value.lower().startswith(("your-", "replace-", "https://your-"))]
        if missing:
            raise ValueError("Configure " + ", ".join(missing) + " in the root .env or environment.")
        return cls(*values, os.getenv(f"{prefix}_API_VERSION") or versions[service])


def azure_client(service="text"):
    from openai import AzureOpenAI

    settings = AzureSettings.load(service)
    client = AzureOpenAI(azure_endpoint=settings.endpoint, api_key=settings.key,
                         api_version=settings.api_version, timeout=60.0, max_retries=2)
    return client, settings.deployment


def chat(messages):
    client, deployment = azure_client("text")
    response = client.chat.completions.create(model=deployment, messages=messages)
    text = response.choices[0].message.content
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The deployment returned no text response.")
    return text


def image_messages(question, image_path, system=None):
    """Build a vision request with the correct image MIME type and distinct roles."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ValueError("Choose a JPEG, PNG, WEBP, or GIF image.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": [
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
    ]})
    return messages


def transcribe_audio(audio_path, translate=False):
    """Transcribe input-language audio, or use a translation-capable deployment for English."""
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size >= 25 * 1024 * 1024:
        raise ValueError("Use an audio file smaller than 25 MiB for this example.")
    client, deployment = azure_client("asr")
    operation = client.audio.translations if translate else client.audio.transcriptions
    with path.open("rb") as audio:
        response = operation.create(model=deployment, file=audio)
    return response.text


def synthesize_speech(text, output_path, voice="alloy"):
    """Write a new MP3 using the configured Azure TTS deployment name."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Speech input must contain text.")
    path = Path(output_path)
    if path.suffix.lower() != ".mp3":
        raise ValueError("Use an .mp3 output path.")
    client, deployment = azure_client("tts")
    path.parent.mkdir(parents=True, exist_ok=True)
    with client.audio.speech.with_streaming_response.create(
        model=deployment, voice=voice, input=text, response_format="mp3"
    ) as response:
        response.stream_to_file(path)
    return path
