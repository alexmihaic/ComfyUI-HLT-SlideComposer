"""Project-specific exceptions for HLT Slide Composer."""

from __future__ import annotations


MESSAGE_PREFIX = "[HLT Slide Composer]"


class HLTSlideError(Exception):
    """Base error for HLT Slide Composer failures."""


class InvalidTensorError(HLTSlideError):
    """Raised when image tensor or array data has an unsupported shape."""


class InvalidCanvasError(HLTSlideError):
    """Raised when canvas geometry or preset values are invalid."""


def prefixed_message(message: str) -> str:
    return f"{MESSAGE_PREFIX} {message}"
