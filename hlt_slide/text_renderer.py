"""Pillow renderer for future HLT Text Composer layouts."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping, Sequence

from PIL import Image, ImageDraw

from .color_utils import parse_color
from .config import CanvasSize, Rect, resolve_canvas_size
from .image_utils import fit_image_to_box
from .logo_utils import calculate_logo_size, compose_logo
from .text_engine import FittedText, calculate_line_ink_bounds, fit_text
from .text_layouts import (
    DEFAULT_TEXT_ROLES,
    TextCompositionLayout,
    TextLayoutSettings,
    active_text_blocks,
    describe_text_layout,
    select_text_layout,
)


TEXT_COMPOSER_WARNING_PREFIX = "[HLT Text Composer]"
BASE_CANVAS_WIDTH = 1080.0
RGBA = tuple[int, int, int, int]
HorizontalAlign = Literal["left", "center", "right"]
VerticalAlign = Literal["top", "center", "bottom"]


@dataclass(frozen=True)
class TextRoleStyle:
    maximum_font_size: int
    preferred_font_size: int
    minimum_font_size: int
    max_lines: int
    line_spacing: int
    default_color_mode: str = "text"


BASE_ROLE_STYLES: Mapping[str, TextRoleStyle] = MappingProxyType(
    {
        "number": TextRoleStyle(300, 220, 48, 2, 6),
        "headline": TextRoleStyle(220, 168, 40, 4, 8),
        "quote": TextRoleStyle(170, 120, 36, 7, 10),
        "subheadline": TextRoleStyle(150, 104, 30, 5, 8),
        "body": TextRoleStyle(100, 68, 24, 10, 8),
        "label": TextRoleStyle(82, 56, 20, 3, 5),
        "caption": TextRoleStyle(68, 44, 18, 4, 5),
    }
)


@dataclass(frozen=True)
class TextRenderSettings:
    canvas_preset: str = "9:16 Social · 1080x1920"
    custom_width: int = 1080
    custom_height: int = 1920
    layout: str = "auto_text"
    layout_settings: TextLayoutSettings = TextLayoutSettings()
    background_mode: str = "solid"
    background_color: str = "#000000"
    background_fit: str = "cover"
    background_opacity: float = 1.0
    overlay_opacity: float = 0.0
    font_path: str | None = None
    font_scale: float = 1.0
    text_color: str = "#F3F0E8"
    accent_color: str = "#E92124"
    accent_target: str = "none"
    horizontal_align: str = "auto"
    vertical_align: str = "auto"
    uppercase: bool = False
    clipping: bool = True
    break_long_words: bool = False
    warn_on_truncation: bool = True
    logo_width_percent: float = 18.0
    logo_max_height_percent: float = 8.0
    logo_opacity: float = 1.0
    logo_bottom_offset: int = 0
    invert_logo_mask: bool = True
    reserve_logo_space: bool = False
    logo_gap: int = 24
    debug_layout: bool = False

    def __post_init__(self) -> None:
        if not 0.25 <= self.font_scale <= 4.0:
            raise ValueError("font_scale must be between 0.25 and 4.0.")
        if self.background_mode not in {"solid", "image", "image_with_overlay"}:
            raise ValueError("background_mode must be solid, image or image_with_overlay.")
        if self.background_fit not in {"cover", "contain", "stretch"}:
            raise ValueError("background_fit must be cover, contain or stretch.")
        if self.accent_target not in {"none", "first_active", "text_1", "text_2", "text_3", "text_4"}:
            raise ValueError("accent_target is not supported.")
        if self.horizontal_align not in {"auto", "left", "center", "right"}:
            raise ValueError("horizontal_align must be auto, left, center or right.")
        if self.vertical_align not in {"auto", "top", "center", "bottom"}:
            raise ValueError("vertical_align must be auto, top, center or bottom.")


@dataclass(frozen=True)
class FittedTextBlock:
    source_index: int
    role: str
    original_text: str
    rendered_text: str
    rect: Rect
    inner_rect: Rect
    font_size: int
    line_count: int
    alignment: str
    vertical_alignment: str
    color: RGBA
    was_truncated: bool
    preferred_font_size: int
    maximum_font_size: int
    text_width_usage_percentage: float
    text_height_usage_percentage: float
    preserve_words: bool
    fitted_text: FittedText


@dataclass(frozen=True)
class TextCompositionRenderPlan:
    geometry: TextCompositionLayout
    fitted_blocks: tuple[FittedTextBlock, ...]
    canvas_size: CanvasSize
    logo_rect: Rect | None
    diagnostics: Mapping[str, object]


def scaled_role_style(role: str, canvas_size: CanvasSize, *, font_scale: float = 1.0) -> TextRoleStyle:
    if role not in BASE_ROLE_STYLES:
        raise ValueError(f"Unknown text role: {role!r}.")
    if not 0.25 <= font_scale <= 4.0:
        raise ValueError("font_scale must be between 0.25 and 4.0.")
    base = BASE_ROLE_STYLES[role]
    scale = (canvas_size.width / BASE_CANVAS_WIDTH) * font_scale
    return TextRoleStyle(
        maximum_font_size=max(1, round(base.maximum_font_size * scale)),
        preferred_font_size=max(1, round(base.preferred_font_size * scale)),
        minimum_font_size=max(1, round(base.minimum_font_size * scale)),
        max_lines=base.max_lines,
        line_spacing=max(0, round(base.line_spacing * scale)),
        default_color_mode=base.default_color_mode,
    )


def measure_text_composition(
    texts: Sequence[str],
    *,
    roles: Sequence[str] | None = None,
    canvas_size: CanvasSize | None = None,
    settings: TextRenderSettings | None = None,
    background_image: Image.Image | None = None,
    logo_image: Image.Image | None = None,
    logo_mask: Image.Image | None = None,
) -> TextCompositionRenderPlan:
    render_settings = settings or TextRenderSettings()
    resolved_canvas = _resolve_canvas(canvas_size, render_settings, background_image)
    source_blocks = active_text_blocks(texts, roles or DEFAULT_TEXT_ROLES[: len(texts)])
    logo_rect = _measure_logo_rect(resolved_canvas, render_settings, logo_image, logo_mask)
    layout_settings = _effective_layout_settings(render_settings, resolved_canvas, logo_rect)
    geometry = select_text_layout(
        resolved_canvas,
        source_blocks,
        layout_settings,
        render_settings.layout,
    )
    accent_index = _resolve_accent_source_index(render_settings.accent_target, source_blocks)
    fitted_blocks = tuple(
        _fit_block(position, block, layout_block, geometry, render_settings, resolved_canvas, accent_index)
        for position, (block, layout_block) in enumerate(zip(source_blocks, geometry.blocks))
    )
    diagnostics = MappingProxyType(
        {
            "layout": describe_text_layout(geometry),
            "accent_source_index": accent_index,
            "logo_reserved": render_settings.reserve_logo_space and logo_rect is not None,
            "debug_layout": render_settings.debug_layout,
            "block_metrics": tuple(
                {
                    "source_index": block.source_index,
                    "role": block.role,
                    "preferred_font_size": block.preferred_font_size,
                    "maximum_font_size": block.maximum_font_size,
                    "selected_font_size": block.font_size,
                    "text_width_usage_percentage": block.text_width_usage_percentage,
                    "text_height_usage_percentage": block.text_height_usage_percentage,
                    "preserve_words": block.preserve_words,
                    "was_truncated": block.was_truncated,
                }
                for block in fitted_blocks
            ),
        }
    )
    return TextCompositionRenderPlan(
        geometry=geometry,
        fitted_blocks=fitted_blocks,
        canvas_size=resolved_canvas,
        logo_rect=logo_rect,
        diagnostics=diagnostics,
    )


def render_text_composition(
    texts: Sequence[str],
    *,
    roles: Sequence[str] | None = None,
    canvas_size: CanvasSize | None = None,
    settings: TextRenderSettings | None = None,
    background_image: Image.Image | None = None,
    logo_image: Image.Image | None = None,
    logo_mask: Image.Image | None = None,
) -> Image.Image:
    render_settings = settings or TextRenderSettings()
    plan = measure_text_composition(
        texts,
        roles=roles,
        canvas_size=canvas_size,
        settings=render_settings,
        background_image=background_image,
        logo_image=logo_image,
        logo_mask=logo_mask,
    )
    output = _draw_background(plan.canvas_size, render_settings, background_image)
    for block in plan.fitted_blocks:
        output = _draw_fitted_block(output, block, clipping=render_settings.clipping)
    output = _draw_logo(output, plan, render_settings, logo_image, logo_mask)
    if render_settings.debug_layout:
        _draw_debug(output, plan)
    return output.convert("RGB")


def _resolve_canvas(
    canvas_size: CanvasSize | None,
    settings: TextRenderSettings,
    background_image: Image.Image | None,
) -> CanvasSize:
    if canvas_size is not None:
        return canvas_size
    background_size = (
        CanvasSize(background_image.width, background_image.height)
        if background_image is not None
        else None
    )
    resolved = resolve_canvas_size(
        settings.canvas_preset,
        custom_width=settings.custom_width,
        custom_height=settings.custom_height,
        background_size=background_size,
    )
    for warning in resolved.warnings:
        warnings.warn(warning.replace("[HLT Slide Composer]", TEXT_COMPOSER_WARNING_PREFIX), stacklevel=3)
    return resolved.size


def _measure_logo_rect(
    canvas_size: CanvasSize,
    settings: TextRenderSettings,
    logo_image: Image.Image | None,
    logo_mask: Image.Image | None,
) -> Rect | None:
    if logo_image is None:
        return None
    width, height = calculate_logo_size(
        logo_image,
        canvas_size,
        logo_width_percent=settings.logo_width_percent,
        logo_max_height_percent=settings.logo_max_height_percent,
    )
    scale = canvas_size.width / BASE_CANVAS_WIDTH
    bottom_offset = round(settings.logo_bottom_offset * scale)
    x = (canvas_size.width - width) // 2
    y = canvas_size.height - height - bottom_offset - round(24 * scale)
    return Rect(x, max(0, y), width, height)


def _effective_layout_settings(
    settings: TextRenderSettings,
    canvas_size: CanvasSize,
    logo_rect: Rect | None,
) -> TextLayoutSettings:
    layout = settings.layout_settings
    if not settings.reserve_logo_space or logo_rect is None:
        return layout
    scale = canvas_size.width / BASE_CANVAS_WIDTH
    reserved_pixels = max(0, canvas_size.height - logo_rect.y) + round(settings.logo_gap * scale)
    reserved = round(reserved_pixels / scale) if scale > 0 else reserved_pixels
    return TextLayoutSettings(
        outer_margin=layout.outer_margin,
        top_margin=layout.top_margin,
        bottom_margin=layout.bottom_margin + reserved,
        block_gap=layout.block_gap,
        inner_padding=layout.inner_padding,
        minimum_block_width=layout.minimum_block_width,
        minimum_block_height=layout.minimum_block_height,
        split_axis=layout.split_axis,
    )


def _resolve_accent_source_index(
    accent_target: str,
    source_blocks: Sequence,
) -> int | None:
    if accent_target == "none":
        return None
    if accent_target == "first_active":
        return source_blocks[0].source_index
    source_index = int(accent_target.removeprefix("text_")) - 1
    if any(block.source_index == source_index for block in source_blocks):
        return source_index
    warnings.warn(
        f"{TEXT_COMPOSER_WARNING_PREFIX} accent_target='{accent_target}' selected an empty text slot; no accent was applied.",
        stacklevel=3,
    )
    return None


def _fit_block(
    position: int,
    source_block,
    layout_block,
    geometry: TextCompositionLayout,
    settings: TextRenderSettings,
    canvas_size: CanvasSize,
    accent_index: int | None,
) -> FittedTextBlock:
    style = scaled_role_style(source_block.role, canvas_size, font_scale=settings.font_scale)
    original_text = source_block.text
    text_for_render = original_text.upper() if settings.uppercase else original_text
    fitted = _fit_text_largest(
        text_for_render,
        font_path=settings.font_path,
        maximum_size=style.maximum_font_size,
        minimum_size=style.minimum_font_size,
        max_width=layout_block.inner_rect.width,
        max_height=layout_block.inner_rect.height,
        max_lines=style.max_lines,
        line_spacing=style.line_spacing,
        break_long_words=settings.break_long_words,
    )
    if fitted.was_truncated and settings.warn_on_truncation:
        warnings.warn(
            f"{TEXT_COMPOSER_WARNING_PREFIX} text_{source_block.source_index + 1} was truncated.",
            stacklevel=4,
        )
    alignment, vertical_alignment = _resolved_alignment(geometry.effective_layout, len(geometry.blocks), position, settings)
    color = parse_color(settings.accent_color if source_block.source_index == accent_index else settings.text_color)
    return FittedTextBlock(
        source_index=source_block.source_index,
        role=source_block.role,
        original_text=original_text,
        rendered_text="\n".join(fitted.lines),
        rect=layout_block.rect,
        inner_rect=layout_block.inner_rect,
        font_size=fitted.font_size,
        line_count=len(fitted.lines),
        alignment=alignment,
        vertical_alignment=vertical_alignment,
        color=color,
        was_truncated=fitted.was_truncated,
        preferred_font_size=style.preferred_font_size,
        maximum_font_size=style.maximum_font_size,
        text_width_usage_percentage=_usage(fitted.width, layout_block.inner_rect.width),
        text_height_usage_percentage=_usage(fitted.height, layout_block.inner_rect.height),
        preserve_words=not settings.break_long_words,
        fitted_text=fitted,
    )


def _fit_text_largest(
    text: str,
    *,
    font_path: str | None,
    maximum_size: int,
    minimum_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    line_spacing: int,
    break_long_words: bool,
) -> FittedText:
    best_truncated: FittedText | None = None
    for size in range(maximum_size, minimum_size - 1, -1):
        fitted = fit_text(
            text,
            font_path=font_path,
            preferred_size=size,
            minimum_size=size,
            max_width=max_width,
            max_height=max_height,
            max_lines=max_lines,
            line_spacing=line_spacing,
            uppercase=False,
            break_long_words=break_long_words,
        )
        if not fitted.was_truncated and fitted.width <= max_width and fitted.height <= max_height:
            return fitted
        if best_truncated is None or fitted.font_size < best_truncated.font_size:
            best_truncated = fitted
    if best_truncated is None:
        raise ValueError("Unable to fit text.")
    return best_truncated


def _usage(used: int, available: int) -> float:
    if available <= 0:
        return 0.0
    return round(min(100.0, (used / available) * 100.0), 6)


def _resolved_alignment(
    layout_name: str,
    block_count: int,
    position: int,
    settings: TextRenderSettings,
) -> tuple[HorizontalAlign, VerticalAlign]:
    if settings.horizontal_align == "auto":
        horizontal: HorizontalAlign = "center" if layout_name == "centered_statement" else "left"
        if layout_name == "editorial_quote" and block_count == 2 and position == 1:
            horizontal = "right"
    else:
        horizontal = settings.horizontal_align  # type: ignore[assignment]

    if settings.vertical_align == "auto":
        vertical: VerticalAlign = "center"
        if layout_name == "editorial_quote" and block_count == 2 and position == 1:
            vertical = "bottom"
    else:
        vertical = settings.vertical_align  # type: ignore[assignment]
    return horizontal, vertical


def _draw_background(
    canvas_size: CanvasSize,
    settings: TextRenderSettings,
    background_image: Image.Image | None,
) -> Image.Image:
    base_color = parse_color(settings.background_color)[:3]
    output = Image.new("RGB", (canvas_size.width, canvas_size.height), base_color)
    if settings.background_mode == "solid":
        return output
    if background_image is None:
        warnings.warn(
            f"{TEXT_COMPOSER_WARNING_PREFIX} no background_image was provided; using solid background.",
            stacklevel=3,
        )
        return output
    fitted = fit_image_to_box(
        background_image,
        (canvas_size.width, canvas_size.height),
        fit=settings.background_fit,
        contain_fill_mode="cell_color",
        cell_background_color=parse_color(settings.background_color),
    ).convert("RGB")
    output = Image.blend(output, fitted, _clamp(settings.background_opacity))
    if settings.background_mode == "image_with_overlay":
        overlay = Image.new("RGB", output.size, base_color)
        output = Image.blend(output, overlay, _clamp(settings.overlay_opacity))
    return output


def _draw_fitted_block(image: Image.Image, block: FittedTextBlock, *, clipping: bool) -> Image.Image:
    if not block.fitted_text.lines:
        return image.copy()
    target_rect = Rect(0, 0, block.inner_rect.width, block.inner_rect.height) if clipping else block.inner_rect
    draw_target = Image.new("RGBA", (block.inner_rect.width, block.inner_rect.height), (0, 0, 0, 0)) if clipping else image.convert("RGBA")
    draw = ImageDraw.Draw(draw_target)
    y = _aligned_top(target_rect, block.fitted_text.height, block.vertical_alignment)
    for line in block.fitted_text.lines:
        bounds = calculate_line_ink_bounds(line, block.fitted_text.font)
        x = _aligned_left(target_rect, bounds.width, bounds.left, block.alignment)
        draw.text((round(x), round(y - bounds.top)), line, font=block.fitted_text.font, fill=block.color)
        y += bounds.height + _line_spacing(block)
    if not clipping:
        return draw_target.convert(image.mode)
    base = image.convert("RGBA")
    base.alpha_composite(draw_target, (block.inner_rect.x, block.inner_rect.y))
    return base.convert(image.mode)


def _line_spacing(block: FittedTextBlock) -> int:
    if block.line_count <= 1:
        return 0
    if block.fitted_text.height <= 0:
        return 0
    line_heights = sum(calculate_line_ink_bounds(line, block.fitted_text.font).height for line in block.fitted_text.lines)
    return max(0, (block.fitted_text.height - line_heights) // (block.line_count - 1))


def _aligned_left(rect: Rect, width: int, left_offset: int, alignment: str) -> float:
    if alignment == "left":
        return rect.x - left_offset
    if alignment == "right":
        return rect.right - width - left_offset
    return rect.x + ((rect.width - width) / 2) - left_offset


def _aligned_top(rect: Rect, height: int, alignment: str) -> float:
    if alignment == "top":
        return float(rect.y)
    if alignment == "bottom":
        return float(rect.bottom - height)
    return rect.y + ((rect.height - height) / 2)


def _draw_logo(
    output: Image.Image,
    plan: TextCompositionRenderPlan,
    settings: TextRenderSettings,
    logo_image: Image.Image | None,
    logo_mask: Image.Image | None,
) -> Image.Image:
    if logo_image is None or plan.logo_rect is None:
        return output
    footer_rect = Rect(0, plan.logo_rect.y, plan.canvas_size.width, plan.canvas_size.height - plan.logo_rect.y)
    return compose_logo(
        output,
        logo_image,
        canvas_size=plan.canvas_size,
        footer_rect=footer_rect,
        logo_mask=logo_mask,
        logo_width_percent=settings.logo_width_percent,
        logo_max_height_percent=settings.logo_max_height_percent,
        logo_opacity=settings.logo_opacity,
        logo_bottom_offset=settings.logo_bottom_offset,
        invert_logo_mask=settings.invert_logo_mask,
    )


def _draw_debug(output: Image.Image, plan: TextCompositionRenderPlan) -> None:
    draw = ImageDraw.Draw(output)
    draw.text((8, 8), "TEXT COMPOSER", fill=(255, 255, 0))
    draw.text((8, 22), plan.geometry.requested_layout, fill=(255, 255, 0))
    draw.text((8, 36), plan.geometry.effective_layout, fill=(255, 255, 0))
    _debug_rect(draw, plan.geometry.content_rect, "content", (120, 120, 120), width=2)
    for block in plan.fitted_blocks:
        _debug_rect(draw, block.rect, f"text_{block.source_index + 1} {block.role}", (233, 33, 36), width=2)
        _debug_rect(
            draw,
            block.inner_rect,
            f"pref={block.preferred_font_size} max={block.maximum_font_size} sel={block.font_size}",
            (0, 180, 255),
            width=1,
        )
        draw.text(
            (block.rect.x + 4, block.rect.y + 18),
            (
                f"{block.alignment}/{block.vertical_alignment} "
                f"{block.line_count}l trunc={block.was_truncated} "
                f"w={block.text_width_usage_percentage:.1f}% "
                f"h={block.text_height_usage_percentage:.1f}% "
                f"preserve_words={block.preserve_words}"
            ),
            fill=(255, 255, 0),
        )
    if plan.logo_rect is not None:
        _debug_rect(draw, plan.logo_rect, "logo", (255, 128, 0), width=2)


def _debug_rect(draw: ImageDraw.ImageDraw, rect: Rect, label: str, color: tuple[int, int, int], *, width: int) -> None:
    draw.rectangle((rect.x, rect.y, rect.right - 1, rect.bottom - 1), outline=color, width=width)
    draw.text((rect.x + 4, rect.y + 4), label, fill=color)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
