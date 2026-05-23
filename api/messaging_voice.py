"""Messaging ASR wiring (composition root): default NVIDIA NIM shim for Telegram/Discord."""

from typing import TYPE_CHECKING

from config.settings import Settings

if TYPE_CHECKING:
    from messaging.platforms.base import MessagingPlatform


def bootstrap_optional_messaging_platform(
    settings: Settings,
) -> MessagingPlatform | None:
    """Return Telegram/Discord platform when configured; injects ``TranscriptionBackend``."""
    from messaging.bootstrap import create_optional_messaging_platform
    from providers.nvidia_nim.transcription_backend import NvidiaNimTranscriptionBackend

    return create_optional_messaging_platform(
        settings,
        nim_transcription_backend=NvidiaNimTranscriptionBackend(),
    )
