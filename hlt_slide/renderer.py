"""Pure Pillow renderer for slide layouts."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .adaptive_mosaic import (
    AdaptiveMosaicSettings,
    MosaicCandidate,
    SourceImageInfo,
    select_adaptive_mosaic,
)
from .color_utils import parse_color
from .config import CanvasSize, Rect, resolve_canvas_size
from .exceptions import HLTSlideError, prefixed_message
from .image_utils import compose_image_in_rect, fit_image_to_box
from .layouts import (
    GridMetrics,
    SlideLayout,
    VerticalStackMetrics,
    calculate_grid_2x2,
    calculate_vertical_stack,
    select_auto_social_layout,
)
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
    contain_fill_mode: str = "transparent"
    font_path: str | None = None
    title_font_size: int = 64
    label_font_size: int = 34
    minimum_font_size: int = 18
    line_spacing: int = 8
    max_title_lines: int = 2
    max_label_lines: int = 2
    uppercase_title: bool = True
    uppercase_labels: bool = False
    outer_margin: int = 64
    top_margin: int = 60
    bottom_margin: int = 54
    title_gap: int = 36
    block_gap: int = 30
    image_label_gap: int = 14
    label_padding_top: int = 6
    label_padding_bottom: int = 10
    label_after_gap: int = 20
    label_min_height: int = 32
    label_vertical_align: str = "center"
    label_clip: bool = True
    inner_padding: int = 30
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
    layout: str = "vertical_stack"


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
    effective_layout = _resolve_layout(render_settings.layout, len(active_items))
    title_fit = _measure_title(title, render_settings, content_width)
    label_widths = _label_measure_widths(effective_layout, len(active_items), canvas_size, render_settings)
    label_fits = _measure_labels(active_items, render_settings, label_widths)
    footer_height = _resolved_footer_height(canvas_size, render_settings, logo_image)
    reserve_footer = render_settings.reserve_footer or logo_image is not None

    layout = _calculate_layout(
        effective_layout,
        canvas_size,
        render_settings=render_settings,
        image_count=len(active_items),
        title_height=title_fit.height if title_fit is not None else 0,
        label_heights=tuple(_reserved_label_height(label, render_settings) for label in label_fits),
        reserve_footer=reserve_footer,
        footer_height=footer_height,
    )

    output = _draw_background(canvas_size, render_settings, background_image)
    output = _draw_images(output, active_items, layout, render_settings)
    output = _draw_title(output, title, layout, render_settings)
    output = _draw_labels(output, active_items, layout, render_settings)
    output = _draw_logo(output, canvas_size, layout, render_settings, logo_image, logo_mask)
    if render_settings.debug_layout:
        _draw_debug(
            output,
            layout,
            canvas_size,
            render_settings,
            logo_image,
            logo_mask,
            effective_layout=effective_layout,
        )
    return output.convert("RGB")


def render_adaptive_mosaic(
    items: list[SlideItem] | tuple[SlideItem, ...],
    *,
    title: str = "",
    canvas_size: CanvasSize | None = CanvasSize(1080, 1920),
    settings: RenderSettings | None = None,
    background_image: Image.Image | None = None,
    logo_image: Image.Image | None = None,
    logo_mask: Image.Image | None = None,
    adaptive_settings: AdaptiveMosaicSettings | None = None,
) -> Image.Image:
    render_settings = settings or RenderSettings()
    canvas_size = _resolve_canvas_size(canvas_size, render_settings, background_image)
    active_items = _active_items(items, "adaptive_mosaic")
    layout, candidate = measure_adaptive_mosaic_layout(
        active_items,
        title=title,
        canvas_size=canvas_size,
        settings=render_settings,
        logo_image=logo_image,
        adaptive_settings=adaptive_settings,
    )

    output = _draw_background(canvas_size, render_settings, background_image)
    output = _draw_adaptive_images(output, active_items, layout, render_settings)
    output = _draw_title(output, title, layout, render_settings)
    output = _draw_labels(output, active_items, layout, render_settings)
    output = _draw_logo(output, canvas_size, layout, render_settings, logo_image, logo_mask)
    if render_settings.debug_layout:
        _draw_debug(
            output,
            layout,
            canvas_size,
            render_settings,
            logo_image,
            logo_mask,
            effective_layout="adaptive_mosaic",
            candidate=candidate,
            strategy=(adaptive_settings or AdaptiveMosaicSettings()).strategy,
        )
    return output.convert("RGB")


def measure_adaptive_mosaic_layout(
    items: list[SlideItem] | tuple[SlideItem, ...],
    *,
    title: str = "",
    canvas_size: CanvasSize = CanvasSize(1080, 1920),
    settings: RenderSettings | None = None,
    logo_image: Image.Image | None = None,
    adaptive_settings: AdaptiveMosaicSettings | None = None,
) -> tuple[SlideLayout, MosaicCandidate]:
    render_settings = settings or RenderSettings()
    active_items = _active_items(items, "adaptive_mosaic")
    mosaic_settings = _adaptive_settings_from_render_settings(
        render_settings, adaptive_settings
    )
    sources = _source_infos(active_items)
    title_fit = _measure_title(
        title,
        render_settings,
        _content_width(canvas_size, render_settings),
    )
    footer_height = _resolved_footer_height(canvas_size, render_settings, logo_image)
    reserve_footer = render_settings.reserve_footer or logo_image is not None
    title_rect, footer_rect, content_rect = _adaptive_content_rects(
        canvas_size,
        render_settings,
        title_height=title_fit.height if title_fit is not None else 0,
        footer_height=footer_height,
        reserve_footer=reserve_footer,
    )
    label_heights = tuple(
        mosaic_settings.label_min_height if item.label.strip() else 0
        for item in active_items
    )
    layout: SlideLayout | None = None
    candidate: MosaicCandidate | None = None
    for _iteration in range(3):
        layout, candidate = select_adaptive_mosaic(
            canvas_size,
            sources,
            mosaic_settings,
            content_rect=content_rect,
            title_rect=title_rect,
            footer_rect=footer_rect,
            label_heights=label_heights,
        )
        measured = _measure_candidate_label_heights(
            active_items,
            layout,
            render_settings,
        )
        if measured == label_heights:
            break
        label_heights = measured
    if layout is None or candidate is None:
        raise HLTSlideError(prefixed_message("adaptive_mosaic could not produce a layout."))
    return layout, candidate


def _active_items(
    items: list[SlideItem] | tuple[SlideItem, ...],
    layout_name: str,
) -> tuple[SlideItem, ...]:
    active_items = tuple(item for item in items if item.image is not None)
    if not active_items:
        raise HLTSlideError(prefixed_message(f"{layout_name} requires image_1."))
    if len(active_items) > 4:
        raise HLTSlideError(prefixed_message(f"{layout_name} supports at most 4 images."))
    for index, item in enumerate(active_items, start=1):
        if item.image.width < 1 or item.image.height < 1:
            raise HLTSlideError(
                prefixed_message(f"adaptive_mosaic image {index} has invalid dimensions.")
            )
    return active_items


def _source_infos(items: tuple[SlideItem, ...]) -> tuple[SourceImageInfo, ...]:
    return tuple(
        SourceImageInfo(
            index=index,
            width=item.image.width,
            height=item.image.height,
            aspect_ratio=item.image.width / item.image.height,
            has_label=bool(item.label.strip()),
        )
        for index, item in enumerate(items)
    )


def _resolve_layout(requested_layout: str, active_image_count: int) -> str:
    if requested_layout == "auto_social":
        return select_auto_social_layout(active_image_count)
    if requested_layout in {"vertical_stack", "grid_2x2"}:
        return requested_layout
    raise HLTSlideError(prefixed_message(f"Unsupported layout: {requested_layout!r}."))


def _calculate_layout(
    layout_name: str,
    canvas_size: CanvasSize,
    *,
    render_settings: RenderSettings,
    image_count: int,
    title_height: int,
    label_heights: tuple[int, ...],
    reserve_footer: bool,
    footer_height: int,
) -> SlideLayout:
    if layout_name == "vertical_stack":
        return calculate_vertical_stack(
            canvas_size,
            image_count=image_count,
            title_height=title_height,
            label_heights=label_heights,
            reserve_footer=reserve_footer,
            footer_height=footer_height,
            metrics=VerticalStackMetrics(
                outer_margin=render_settings.outer_margin,
                top_margin=render_settings.top_margin,
                bottom_margin=render_settings.bottom_margin,
                title_gap=render_settings.title_gap,
                block_gap=render_settings.block_gap,
                image_label_gap=render_settings.image_label_gap,
                label_after_gap=render_settings.label_after_gap,
                footer_height=footer_height,
            ),
        )
    if layout_name == "grid_2x2":
        return calculate_grid_2x2(
            canvas_size,
            image_count=image_count,
            title_height=title_height,
            label_heights=label_heights,
            reserve_footer=reserve_footer,
            footer_height=footer_height,
            metrics=GridMetrics(
                outer_margin=render_settings.outer_margin,
                top_margin=render_settings.top_margin,
                bottom_margin=render_settings.bottom_margin,
                title_gap=render_settings.title_gap,
                row_gap=render_settings.block_gap,
                column_gap=render_settings.inner_padding,
                image_label_gap=render_settings.image_label_gap,
                label_after_gap=render_settings.label_after_gap,
                footer_height=footer_height,
            ),
        )
    raise HLTSlideError(prefixed_message(f"Unsupported layout: {layout_name!r}."))


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
    max_widths: tuple[int, ...],
) -> tuple[FittedText | None, ...]:
    fits: list[FittedText | None] = []
    for index, item in enumerate(items, start=1):
        if not item.label.strip():
            fits.append(None)
            continue
        max_width = max_widths[index - 1]
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


def _label_measure_widths(
    layout_name: str,
    image_count: int,
    canvas_size: CanvasSize,
    settings: RenderSettings,
) -> tuple[int, ...]:
    scale = canvas_size.width / 1080.0
    content_width = canvas_size.width - (2 * _scaled(settings.outer_margin, scale))
    content_width = max(1, content_width)
    if layout_name == "vertical_stack" or image_count == 1:
        return tuple(content_width for _ in range(image_count))

    column_gap = _scaled(settings.inner_padding, scale)
    column_width = max(1, (content_width - column_gap) // 2)
    if image_count == 2:
        return (column_width, column_width)
    if image_count == 3:
        return (content_width, column_width, column_width)
    return (column_width, column_width, column_width, column_width)


def _adaptive_settings_from_render_settings(
    settings: RenderSettings,
    adaptive_settings: AdaptiveMosaicSettings | None,
) -> AdaptiveMosaicSettings:
    base = adaptive_settings or AdaptiveMosaicSettings()
    return AdaptiveMosaicSettings(
        strategy=base.strategy,
        preserve_order=base.preserve_order,
        preserve_aspect=True,
        hero_index=base.hero_index,
        gap=settings.inner_padding if adaptive_settings is None else base.gap,
        minimum_image_width=base.minimum_image_width,
        minimum_image_height=base.minimum_image_height,
        label_padding_top=settings.label_padding_top,
        label_padding_bottom=settings.label_padding_bottom,
        label_after_gap=settings.image_label_gap,
        label_min_height=settings.label_min_height,
        footer_height=0,
        footer_gap=0,
    )


def _content_width(canvas_size: CanvasSize, settings: RenderSettings) -> int:
    scale = canvas_size.width / 1080.0
    return max(1, canvas_size.width - (2 * _scaled(settings.outer_margin, scale)))


def _adaptive_content_rects(
    canvas_size: CanvasSize,
    settings: RenderSettings,
    *,
    title_height: int,
    footer_height: int,
    reserve_footer: bool,
) -> tuple[Rect | None, Rect | None, Rect]:
    scale = canvas_size.width / 1080.0
    outer_margin = _scaled(settings.outer_margin, scale)
    top_margin = _scaled(settings.top_margin, scale)
    bottom_margin = _scaled(settings.bottom_margin, scale)
    title_gap = _scaled(settings.title_gap, scale)
    content_width = max(1, canvas_size.width - (2 * outer_margin))

    y = top_margin
    title_rect = None
    if title_height > 0:
        title_rect = Rect(outer_margin, y, content_width, title_height)
        y = title_rect.bottom + title_gap

    footer_rect = None
    content_bottom = canvas_size.height - bottom_margin
    if reserve_footer and footer_height > 0:
        footer_rect = Rect(
            outer_margin,
            canvas_size.height - bottom_margin - footer_height,
            content_width,
            footer_height,
        )
        content_bottom = footer_rect.y - bottom_margin

    content_height = content_bottom - y
    if content_height < 1:
        raise HLTSlideError(
            prefixed_message(
                "adaptive_mosaic overflow: title, footer and margins leave no content area."
            )
        )
    return title_rect, footer_rect, Rect(outer_margin, y, content_width, content_height)


def _measure_candidate_label_heights(
    items: tuple[SlideItem, ...],
    layout: SlideLayout,
    settings: RenderSettings,
) -> tuple[int, ...]:
    heights: list[int] = []
    for item, block in zip(items, layout.blocks):
        if not item.label.strip() or block.label_rect is None:
            heights.append(0)
            continue
        max_width = max(1, block.label_rect.width)
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
                prefixed_message(f"La etiqueta {len(heights) + 1} ha sido truncada."),
                stacklevel=3,
            )
        heights.append(_reserved_label_height(fitted, settings))
    return tuple(heights)


def _reserved_label_height(fitted: FittedText | None, settings: RenderSettings) -> int:
    if fitted is None:
        return 0
    return max(
        settings.label_min_height,
        settings.label_padding_top + fitted.height + settings.label_padding_bottom,
    )


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
            contain_fill_mode=settings.contain_fill_mode,
            cell_background_color=parse_color(settings.cell_background_color),
            corner_radius=_scaled(settings.corner_radius, scale),
            border_width=_scaled(settings.border_width, scale),
            border_color=parse_color(settings.border_color),
        )
    return result


def _draw_adaptive_images(
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
            fit="contain",
            crop_anchor="center",
            contain_fill_mode="transparent",
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
        contain_fill_mode="cell_color",
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
        text_rect = _label_text_rect(block.label_rect, settings)
        result = draw_text_in_rect(
            result,
            text_rect,
            item.label,
            font_path=settings.font_path,
            preferred_size=settings.label_font_size,
            minimum_size=settings.minimum_font_size,
            max_lines=settings.max_label_lines,
            line_spacing=settings.line_spacing,
            color=parse_color(settings.label_color),
            uppercase=settings.uppercase_labels,
            vertical_align=_normalized_label_vertical_align(settings.label_vertical_align),
            clip=settings.label_clip,
        )
    return result


def _label_text_rect(label_rect: Rect, settings: RenderSettings) -> Rect:
    top = max(0, settings.label_padding_top)
    bottom = max(0, settings.label_padding_bottom)
    height = max(0, label_rect.height - top - bottom)
    return Rect(label_rect.x, label_rect.y + top, label_rect.width, height)


def _normalized_label_vertical_align(value: str) -> str:
    if value in {"top", "center", "bottom"}:
        return value
    warnings.warn(
        prefixed_message(
            f"label_vertical_align={value!r} no es válido; se usará 'center'."
        ),
        stacklevel=3,
    )
    return "center"


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
    *,
    effective_layout: str,
    candidate: MosaicCandidate | None = None,
    strategy: str | None = None,
) -> None:
    draw = ImageDraw.Draw(output)
    draw.text((8, 8), f"LAYOUT: {effective_layout.upper()}", fill=(255, 255, 0))
    if candidate is not None:
        _draw_adaptive_debug_text(draw, candidate, strategy)
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


def _draw_adaptive_debug_text(
    draw: ImageDraw.ImageDraw,
    candidate: MosaicCandidate,
    strategy: str | None,
) -> None:
    diagnostics = candidate.diagnostics
    lines = (
        f"TEMPLATE: {candidate.template_name}",
        f"STRATEGY: {(strategy or '').upper()}",
        f"SCORE: {candidate.score:.1f}",
        f"UNUSED: {diagnostics.get('unused_area_percentage', 0):.1f}%",
        f"unused_area: {candidate.penalties['unused_area']:.1f}",
        f"tiny_cells: {candidate.penalties['tiny_cells']:.1f}",
        f"visual_imbalance: {candidate.penalties['visual_imbalance']:.1f}",
        f"extreme_size_difference: {candidate.penalties['extreme_size_difference']:.1f}",
        f"label_overflow: {candidate.penalties['label_overflow']:.1f}",
    )
    for index, line in enumerate(lines, start=1):
        draw.text((8, 8 + (index * 12)), line, fill=(255, 255, 0))


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
