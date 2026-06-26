"""Font discovery and loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

from .exceptions import prefixed_message


SYSTEM_FONT_CANDIDATES: tuple[Path, ...] = (
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
)


@dataclass(frozen=True)
class FontResolution:
    font: ImageFont.ImageFont
    path: Path | None
    size: int
    warnings: tuple[str, ...] = ()


def find_system_font_path() -> Path | None:
    for candidate in SYSTEM_FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def resolve_font(font_path: str | Path | None, size: int) -> FontResolution:
    warnings: list[str] = []
    explicit_path = Path(font_path).expanduser() if font_path else None

    if explicit_path is not None:
        if explicit_path.exists():
            return FontResolution(load_font(explicit_path, size), explicit_path, size)
        warnings.append(
            prefixed_message(
                f"Font path {str(explicit_path)!r} was not found; using fallback."
            )
        )

    system_path = find_system_font_path()
    if system_path is not None:
        return FontResolution(
            load_font(system_path, size),
            system_path,
            size,
            tuple(warnings),
        )

    warnings.append(prefixed_message("No TrueType font found; using Pillow default font."))
    return FontResolution(load_font(None, size), None, size, tuple(warnings))


def load_font(path: Path | None, size: int) -> ImageFont.ImageFont:
    return _load_font_cached(str(path) if path is not None else "", int(size))


@lru_cache(maxsize=128)
def _load_font_cached(path: str, size: int) -> ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            return _load_default_font(size)
    return _load_default_font(size)


def _load_default_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()
