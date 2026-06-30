"""Pure text fitting and drawing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

from .config import Rect
from .font_utils import resolve_font


RGBA = tuple[int, int, int, int]
VerticalAlign = Literal["top", "center", "bottom"]
_SPACE_RE = re.compile(r"[ \t\r\f\v]+")


@dataclass(frozen=True)
class FittedText:
    lines: tuple[str, ...]
    font: ImageFont.ImageFont
    font_size: int
    width: int
    height: int
    was_truncated: bool


@dataclass(frozen=True)
class LineInkBounds:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


def fit_text(
    text: str,
    *,
    font_path: str | None,
    preferred_size: int,
    minimum_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    line_spacing: int,
    uppercase: bool = False,
    break_long_words: bool = True,
) -> FittedText:
    cleaned = _clean_text(text, uppercase=uppercase)
    if cleaned == "":
        font = resolve_font(font_path, preferred_size).font
        return FittedText((), font, preferred_size, 0, 0, False)

    for size in range(preferred_size, minimum_size - 1, -1):
        font = resolve_font(font_path, size).font
        lines = _wrap_text(cleaned, font, max_width, break_long_words=break_long_words)
        width, height = _measure_lines(lines, font, line_spacing)
        if len(lines) <= max_lines and width <= max_width and height <= max_height:
            return FittedText(lines, font, size, width, height, False)

    font = resolve_font(font_path, minimum_size).font
    lines = _truncate_text(
        cleaned,
        font,
        max_width,
        max_height,
        max_lines,
        line_spacing,
        break_long_words=break_long_words,
    )
    width, height = _measure_lines(lines, font, line_spacing)
    return FittedText(lines, font, minimum_size, width, height, True)


def draw_text_in_rect(
    image: Image.Image,
    rect: Rect,
    text: str,
    *,
    font_path: str | None,
    preferred_size: int,
    minimum_size: int,
    max_lines: int,
    line_spacing: int,
    color: RGBA,
    uppercase: bool = False,
    vertical_align: VerticalAlign = "center",
    clip: bool = False,
) -> Image.Image:
    target_rect = Rect(0, 0, rect.width, rect.height) if clip else rect
    draw_target = Image.new("RGBA", (rect.width, rect.height), (0, 0, 0, 0)) if clip else image.copy()
    fitted = fit_text(
        text,
        font_path=font_path,
        preferred_size=preferred_size,
        minimum_size=minimum_size,
        max_width=target_rect.width,
        max_height=target_rect.height,
        max_lines=max_lines,
        line_spacing=line_spacing,
        uppercase=uppercase,
    )
    if not fitted.lines:
        return image.copy()

    draw = ImageDraw.Draw(draw_target)
    y = _aligned_top(target_rect, fitted.height, vertical_align)
    for line in fitted.lines:
        bounds = calculate_line_ink_bounds(line, fitted.font)
        x = target_rect.x + ((target_rect.width - bounds.width) / 2) - bounds.left
        draw_y = y - bounds.top
        draw.text((round(x), round(draw_y)), line, font=fitted.font, fill=color)
        y += bounds.height + line_spacing

    if not clip:
        return draw_target

    base = image.convert("RGBA")
    base.alpha_composite(draw_target, (rect.x, rect.y))
    return base if image.mode == "RGBA" else base.convert(image.mode)


def calculate_line_ink_bounds(line: str, font: ImageFont.ImageFont) -> LineInkBounds:
    probe = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(probe)
    left, top, right, bottom = draw.textbbox((0, 0), line or " ", font=font)
    return LineInkBounds(left, top, right, bottom)


def _clean_text(text: str, *, uppercase: bool) -> str:
    lines = [_SPACE_RE.sub(" ", line).strip() for line in text.split("\n")]
    cleaned = "\n".join(lines).strip()
    return cleaned.upper() if uppercase else cleaned


def _wrap_text(
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    *,
    break_long_words: bool = True,
) -> tuple[str, ...]:
    wrapped: list[str] = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            candidate = word if current == "" else f"{current} {word}"
            if _measure_line(candidate, font)[0] <= max_width:
                current = candidate
                continue
            if current:
                wrapped.append(current)
            if _measure_line(word, font)[0] <= max_width:
                current = word
            elif break_long_words:
                pieces = _break_long_word(word, font, max_width)
                wrapped.extend(pieces[:-1])
                current = pieces[-1] if pieces else ""
            else:
                current = word
        if current:
            wrapped.append(current)
    return tuple(wrapped)


def _break_long_word(
    word: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    pieces: list[str] = []
    current = ""
    for char in word:
        candidate = current + char
        if current and _measure_line(candidate, font)[0] > max_width:
            pieces.append(current)
            current = char
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _truncate_text(
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_height: int,
    max_lines: int,
    line_spacing: int,
    *,
    break_long_words: bool = True,
) -> tuple[str, ...]:
    wrapped = list(_wrap_text(text, font, max_width, break_long_words=break_long_words))
    if not wrapped:
        return ()

    allowed_lines = max(1, min(max_lines, _max_lines_for_height(font, max_height, line_spacing)))
    lines = wrapped[:allowed_lines]
    lines[-1] = _truncate_line(lines[-1], font, max_width)
    return tuple(lines)


def _truncate_line(line: str, font: ImageFont.ImageFont, max_width: int) -> str:
    ellipsis = "…"
    if _measure_line(ellipsis, font)[0] > max_width:
        return ""
    candidate = line
    while candidate and _measure_line(candidate + ellipsis, font)[0] > max_width:
        candidate = candidate[:-1]
    return candidate.rstrip() + ellipsis


def _max_lines_for_height(
    font: ImageFont.ImageFont,
    max_height: int,
    line_spacing: int,
) -> int:
    _, line_height = _measure_line("Ag", font)
    if line_height <= 0:
        return 1
    return max(1, (max_height + line_spacing) // (line_height + line_spacing))


def _measure_lines(
    lines: tuple[str, ...],
    font: ImageFont.ImageFont,
    line_spacing: int,
) -> tuple[int, int]:
    if not lines:
        return 0, 0
    sizes = [_measure_line(line, font) for line in lines]
    width = max(line_width for line_width, _ in sizes)
    height = sum(line_height for _, line_height in sizes)
    height += max(0, len(lines) - 1) * line_spacing
    return width, height


def _measure_line(line: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bounds = calculate_line_ink_bounds(line, font)
    return bounds.width, bounds.height


def _aligned_top(rect: Rect, text_height: int, vertical_align: VerticalAlign) -> float:
    if vertical_align == "top":
        return float(rect.y)
    if vertical_align == "bottom":
        return float(rect.bottom - text_height)
    return rect.y + ((rect.height - text_height) / 2)
