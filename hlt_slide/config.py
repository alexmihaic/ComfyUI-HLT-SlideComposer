"""Pure configuration and geometry models."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import InvalidCanvasError, prefixed_message


DEFAULT_CANVAS_SIZE = (1080, 1920)
CUSTOM_PRESET_NAME = "Custom"
BACKGROUND_SIZE_PRESET_NAME = "Background size"


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise InvalidCanvasError(
                prefixed_message("Rect width and height must not be negative.")
            )

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


@dataclass(frozen=True)
class CanvasSize:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise InvalidCanvasError(
                prefixed_message("Canvas width and height must be at least 1 pixel.")
            )


@dataclass(frozen=True)
class ResolutionPreset:
    name: str
    width: int | None
    height: int | None


@dataclass(frozen=True)
class CanvasResolution:
    size: CanvasSize
    warnings: tuple[str, ...] = ()


RESOLUTION_PRESETS: tuple[ResolutionPreset, ...] = (
    ResolutionPreset("9:16 Social · 1080x1920", 1080, 1920),
    ResolutionPreset("9:16 AI · 1152x2048", 1152, 2048),
    ResolutionPreset("9:16 4K · 2160x3840", 2160, 3840),
    ResolutionPreset("4:5 Social · 1080x1350", 1080, 1350),
    ResolutionPreset("3:4 Editorial · 1536x2048", 1536, 2048),
    ResolutionPreset("1:1 Square · 1080x1080", 1080, 1080),
    ResolutionPreset(CUSTOM_PRESET_NAME, None, None),
    ResolutionPreset(BACKGROUND_SIZE_PRESET_NAME, None, None),
)

LEGACY_PRESET_ALIASES = {
    "9:16 Social \u00c2\u00b7 1080x1920": "9:16 Social · 1080x1920",
    "9:16 AI \u00c2\u00b7 1152x2048": "9:16 AI · 1152x2048",
    "9:16 4K \u00c2\u00b7 2160x3840": "9:16 4K · 2160x3840",
    "4:5 Social \u00c2\u00b7 1080x1350": "4:5 Social · 1080x1350",
    "3:4 Editorial \u00c2\u00b7 1536x2048": "3:4 Editorial · 1536x2048",
    "1:1 Square \u00c2\u00b7 1080x1080": "1:1 Square · 1080x1080",
    "9:16 Social \u0100\u00b7 1080x1920": "9:16 Social · 1080x1920",
    "9:16 AI \u0100\u00b7 1152x2048": "9:16 AI · 1152x2048",
    "9:16 4K \u0100\u00b7 2160x3840": "9:16 4K · 2160x3840",
    "4:5 Social \u0100\u00b7 1080x1350": "4:5 Social · 1080x1350",
    "3:4 Editorial \u0100\u00b7 1536x2048": "3:4 Editorial · 1536x2048",
    "1:1 Square \u0100\u00b7 1080x1080": "1:1 Square · 1080x1080",
}

PRESETS_BY_NAME = {preset.name: preset for preset in RESOLUTION_PRESETS}


def resolve_canvas_size(
    preset_name: str,
    *,
    custom_width: int = DEFAULT_CANVAS_SIZE[0],
    custom_height: int = DEFAULT_CANVAS_SIZE[1],
    background_size: CanvasSize | None = None,
) -> CanvasResolution:
    preset_name = LEGACY_PRESET_ALIASES.get(preset_name, preset_name)
    preset = PRESETS_BY_NAME.get(preset_name)
    if preset is None:
        raise InvalidCanvasError(
            prefixed_message(f"Unknown canvas preset: {preset_name!r}.")
        )

    if preset.name == CUSTOM_PRESET_NAME:
        return CanvasResolution(CanvasSize(custom_width, custom_height))

    if preset.name == BACKGROUND_SIZE_PRESET_NAME:
        if background_size is not None:
            return CanvasResolution(background_size)
        warning = prefixed_message(
            "Background size preset selected without a background image; "
            "using 1080x1920."
        )
        return CanvasResolution(CanvasSize(*DEFAULT_CANVAS_SIZE), (warning,))

    if preset.width is None or preset.height is None:
        raise InvalidCanvasError(prefixed_message("Canvas preset is incomplete."))
    return CanvasResolution(CanvasSize(preset.width, preset.height))
