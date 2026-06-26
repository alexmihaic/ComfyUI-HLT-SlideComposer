"""Pure Pillow renderer for vertical stack slides."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .color_utils import parse_color
from .config import CanvasSize, Rect, resolve_canvas_size
from .exceptions import HLTSlideError, prefixed_message
from .image_utils import compose_image_in_rect, fit_image_to_box
from .layouts import SlideLayout, VerticalStackMetrics, calculate_vertical_stack
from .logo_utils import calculate_logo_size, compose_logo, prepare_logo
from .text_engine import FittedText, draw_text_in_rect, fit_text


@dataclass(frozen=True)
class SlideItem:
    image: Image.Image
    label: str = ""


@dataclass(frozen=True)
class RenderSettings:
    canvas_preset: str = "9:16 Social · 1080x1920"
    background_color: str = "#000000"
    background_mode: str = "solid"
    background_fit: str = "cover"
    background_opacity: float = 1.0
    overlay_opacity: float = 0.0
    title_color: str = "#E92124"
    label_color: str = "#E92124"
    border_color: str = "#E92124"
    cell_background_color: str = "#111111"
    font_path: str | None = None
    title_font_size: int = 64
    label_font_size: int = 34
    minimum_font_size: int = 18
    line_spacing: int = 8
    max_title_lines: int = 2
    max_label_lines: int = 2
    uppercase_title: bool = True
    uppercase_labels: bool = False
    image_fit: str = "cover"
    crop_anchor: str = "center"
    corner_radius: int = 18
    border_width: int = 0
    reserve_footer: bool = False
    footer_height: int = 96
    logo_width_percent: float = 18.0
    logo_max_height_percent: float = 8.0
    logo_opacity: float = 1.0
    logo_bottom_offset: int = 0
    invert_logo_mask: bool = True
    debug_layout: bool = False


def render_vertical_stack(
    items: list[SlideItem] | tuple[SlideItem, ...],
    *,
    title: str = "",
    canvas_size: CanvasSize | None = CanvasSize(1080, 1920),
    settings: RenderSettings | None = None,
    background_image: Image.Image | None = None,
    logo_image: Image.Image | None = None,
    logo_mask: Image.Image | None = None,
) -> Image.Image:
    active_items = tuple(item for item in items if item.image is not None)
    if not active_items:
        raise HLTSlideError(prefixed_message("vertical_stack requires image_1."))
    if len(active_items) > 4:
        raise HLTSlideError(prefixed_message("vertical_stack supports at most 4 images."))

    render_settings = settings or RenderSettings()
    canvas_size = _resolve_canvas_size(canvas_size, render_settings, background_image)
    scale = canvas_size.width / 1080.0
    content_width = canvas_size.width - (2 * _scaled(64, scale))
    title_fit = _measure_title(title, render_settings, content_width)
    label_fits = _measure_labels(active_items, render_settings, content_width)
    footer_height = _resolved_footer_height(canvas_size, render_settings, logo_image)
    reserve_footer = render_settings.reserve_footer or logo_image is not None

    metrics = VerticalStackMetrics(
        footer_height=footer_height,
        outer_margin=64,
        top_margin=60,
        bottom_margin=54,
        title_gap=36,
        block_gap=30,
        image_label_gap=14,
    )
    layout = calculate_vertical_stack(
        canvas_size,
        image_count=len(active_items),
        title_height=title_fit.height if title_fit is not None else 0,
        label_heights=tuple(label.height if label is not None else 0 for label in label_fits),
        reserve_footer=reserve_footer,
        footer_height=footer_height,
        metrics=metrics,
    )

    output = _draw_background(canvas_size, render_settings, background_image)
    output = _draw_title(output, title, layout, render_settings)
    output = _draw_images(output, active_items, layout, render_settings)
    output = _draw_labels(output, active_items, layout, render_settings)
    output = _draw_logo(output, canvas_size, layout, render_settings, logo_image, logo_mask)
    if render_settings.debug_layout:
        _draw_debug(output, layout, canvas_size, render_settings, logo_image, logo_mask)
    return output.convert("RGB")


def _resolve_canvas_size(
    canvas_size: CanvasSize | None,
    settings: RenderSettings,
    background_image: Image.Image | None,
) -> CanvasSize:
    if canvas_size is not None:
        return canvas_size

    background_size = (
        CanvasSize(background_image.width, background_image.height)
        if background_image is not None
        else None
    )
    resolved = resolve_canvas_size(settings.canvas_preset, background_size=background_size)
    for warning in resolved.warnings:
        warnings.warn(warning, stacklevel=3)
    return resolved.size


def _measure_title(
    title: str,
    settings: RenderSettings,
    max_width: int,
) -> FittedText | None:
    if not title.strip():
        return None
    return fit_text(
        title,
        font_path=settings.font_path,
        preferred_size=settings.title_font_size,
        minimum_size=settings.minimum_font_size,
        max_width=max_width,
        max_height=300,
        max_lines=settings.max_title_lines,
        line_spacing=settings.line_spacing,
        uppercase=settings.uppercase_title,
    )


def _measure_labels(
    items: tuple[SlideItem, ...],
    settings: RenderSettings,
    max_width: int,
) -> tuple[FittedText | None, ...]:
    fits: list[FittedText | None] = []
    for index, item in enumerate(items, start=1):
        if not item.label.strip():
            fits.append(None)
            continue
        fitted = fit_text(
            item.label,
            font_path=settings.font_path,
            preferred_size=settings.label_font_size,
            minimum_size=settings.minimum_font_size,
            max_width=max_width,
            max_height=180,
            max_lines=settings.max_label_lines,
            line_spacing=settings.line_spacing,
            uppercase=settings.uppercase_labels,
        )
        if fitted.was_truncated:
            warnings.warn(
                prefixed_message(f"La etiqueta {index} ha sido truncada."),
                stacklevel=3,
            )
        fits.append(fitted)
    return tuple(fits)


def _draw_images(
    output: Image.Image,
    items: tuple[SlideItem, ...],
    layout: SlideLayout,
    settings: RenderSettings,
) -> Image.Image:
    result = output
    scale = output.width / 1080.0
    for item, block in zip(items, layout.blocks):
        result = compose_image_in_rect(
            result,
            item.image,
            block.image_rect,
            fit=settings.image_fit,
            crop_anchor=settings.crop_anchor,
            cell_background_color=parse_color(settings.cell_background_color),
            corner_radius=_scaled(settings.corner_radius, scale),
            border_width=_scaled(settings.border_width, scale),
            border_color=parse_color(settings.border_color),
        )
    return result


def _draw_background(
    canvas_size: CanvasSize,
    settings: RenderSettings,
    background_image: Image.Image | None,
) -> Image.Image:
    base_color = parse_color(settings.background_color)[:3]
    output = Image.new("RGB", (canvas_size.width, canvas_size.height), base_color)
    if settings.background_mode == "solid":
        return output

    if background_image is None:
        warnings.warn(
            prefixed_message("No se proporcionó una imagen de fondo; se usará el color sólido."),
            stacklevel=3,
        )
        return output

    fitted = fit_image_to_box(
        background_image,
        (canvas_size.width, canvas_size.height),
        fit=settings.background_fit,
        cell_background_color=parse_color(settings.background_color),
    ).convert("RGB")
    opacity = _clamp(settings.background_opacity)
    output = Image.blend(output, fitted, opacity)

    if settings.background_mode == "image_with_overlay":
        overlay = Image.new("RGB", output.size, base_color)
        output = Image.blend(output, overlay, _clamp(settings.overlay_opacity))
    elif settings.background_mode != "image":
        raise HLTSlideError(
            prefixed_message(f"Unsupported background mode: {settings.background_mode!r}.")
        )
    return output


def _draw_title(
    output: Image.Image,
    title: str,
    layout: SlideLayout,
    settings: RenderSettings,
) -> Image.Image:
    result = output
    if layout.title_rect is not None:
        result = draw_text_in_rect(
            result,
            layout.title_rect,
            title,
            font_path=settings.font_path,
            preferred_size=settings.title_font_size,
            minimum_size=settings.minimum_font_size,
            max_lines=settings.max_title_lines,
            line_spacing=settings.line_spacing,
            color=parse_color(settings.title_color),
            uppercase=settings.uppercase_title,
        )
    return result


def _draw_labels(
    output: Image.Image,
    items: tuple[SlideItem, ...],
    layout: SlideLayout,
    settings: RenderSettings,
) -> Image.Image:
    result = output
    for item, block in zip(items, layout.blocks):
        if block.label_rect is None:
            continue
        result = draw_text_in_rect(
            result,
            block.label_rect,
            item.label,
            font_path=settings.font_path,
            preferred_size=settings.label_font_size,
            minimum_size=settings.minimum_font_size,
            max_lines=settings.max_label_lines,
            line_spacing=settings.line_spacing,
            color=parse_color(settings.label_color),
            uppercase=settings.uppercase_labels,
        )
    return result


def _draw_logo(
    output: Image.Image,
    canvas_size: CanvasSize,
    layout: SlideLayout,
    settings: RenderSettings,
    logo_image: Image.Image | None,
    logo_mask: Image.Image | None,
) -> Image.Image:
    if logo_image is None or layout.footer_rect is None:
        return output
    return compose_logo(
        output,
        logo_image,
        canvas_size=canvas_size,
        footer_rect=layout.footer_rect,
        logo_mask=logo_mask,
        logo_width_percent=settings.logo_width_percent,
        logo_max_height_percent=settings.logo_max_height_percent,
        logo_opacity=settings.logo_opacity,
        logo_bottom_offset=settings.logo_bottom_offset,
        invert_logo_mask=settings.invert_logo_mask,
    )


def _draw_debug(
    output: Image.Image,
    layout: SlideLayout,
    canvas_size: CanvasSize,
    settings: RenderSettings,
    logo_image: Image.Image | None,
    logo_mask: Image.Image | None,
) -> None:
    draw = ImageDraw.Draw(output)
    if layout.title_rect is not None:
        _debug_rect(draw, layout.title_rect, "TITLE", (255, 255, 0))
    for index, block in enumerate(layout.blocks, start=1):
        _debug_rect(draw, block.image_rect, f"IMAGE {index}", (0, 160, 255))
        if block.label_rect is not None:
            _debug_rect(draw, block.label_rect, f"LABEL {index}", (255, 0, 255))
    if layout.footer_rect is not None:
        _debug_rect(draw, layout.footer_rect, "FOOTER", (0, 255, 255))
        prepared = prepare_logo(
            logo_image,
            canvas_size=canvas_size,
            footer_rect=layout.footer_rect,
            logo_mask=logo_mask,
            logo_width_percent=settings.logo_width_percent,
            logo_max_height_percent=settings.logo_max_height_percent,
            logo_opacity=settings.logo_opacity,
            logo_bottom_offset=settings.logo_bottom_offset,
            invert_logo_mask=settings.invert_logo_mask,
        )
        if prepared is not None:
            _debug_rect(draw, prepared.rect, "LOGO", (255, 128, 0))


def _debug_rect(draw: ImageDraw.ImageDraw, rect: Rect, label: str, color: tuple[int, int, int]) -> None:
    draw.rectangle((rect.x, rect.y, rect.right - 1, rect.bottom - 1), outline=color, width=2)
    draw.text((rect.x + 4, rect.y + 4), f"{label} {rect.width}x{rect.height}", fill=color)


def _scaled(value: int, scale: float) -> int:
    return max(0, round(value * scale))


def _resolved_footer_height(
    canvas_size: CanvasSize,
    settings: RenderSettings,
    logo_image: Image.Image | None,
) -> int:
    manual = settings.footer_height if settings.reserve_footer else 0
    if logo_image is None:
        return manual

    _, logo_height = calculate_logo_size(
        logo_image,
        canvas_size,
        logo_width_percent=settings.logo_width_percent,
        logo_max_height_percent=settings.logo_max_height_percent,
    )
    padding = _scaled(24, canvas_size.width / 1080.0)
    return max(manual, logo_height + (2 * padding))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
