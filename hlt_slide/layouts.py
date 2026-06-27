"""Pure layout geometry calculations."""

from __future__ import annotations

from dataclasses import dataclass

from .config import CanvasSize, Rect
from .exceptions import HLTSlideError, LayoutOverflowError, prefixed_message


BASE_CANVAS_WIDTH = 1080.0


@dataclass(frozen=True)
class BlockLayout:
    image_rect: Rect
    label_rect: Rect | None


@dataclass(frozen=True)
class SlideLayout:
    title_rect: Rect | None
    blocks: tuple[BlockLayout, ...]
    footer_rect: Rect | None


@dataclass(frozen=True)
class VerticalStackMetrics:
    outer_margin: int = 64
    top_margin: int = 60
    bottom_margin: int = 54
    title_gap: int = 36
    block_gap: int = 30
    image_label_gap: int = 14
    label_after_gap: int = 20
    footer_height: int = 0
    min_title_gap: int = 8
    min_block_gap: int = 8
    min_image_label_gap: int = 4
    min_label_after_gap: int = 0


@dataclass(frozen=True)
class GridMetrics:
    outer_margin: int = 64
    top_margin: int = 60
    bottom_margin: int = 54
    title_gap: int = 36
    row_gap: int = 30
    column_gap: int = 30
    image_label_gap: int = 14
    label_after_gap: int = 20
    footer_height: int = 0
    min_title_gap: int = 8
    min_row_gap: int = 8
    min_column_gap: int = 8
    min_image_label_gap: int = 4
    min_label_after_gap: int = 0


def select_auto_social_layout(active_image_count: int) -> str:
    if active_image_count < 1 or active_image_count > 4:
        raise HLTSlideError(
            prefixed_message(
                f"auto_social requires 1 to 4 active images, got {active_image_count}."
            )
        )
    if active_image_count == 4:
        return "grid_2x2"
    return "vertical_stack"


def calculate_vertical_stack(
    canvas_size: CanvasSize,
    *,
    image_count: int,
    title_height: int = 0,
    label_heights: tuple[int, ...] = (),
    reserve_footer: bool = False,
    footer_height: int = 0,
    metrics: VerticalStackMetrics | None = None,
) -> SlideLayout:
    if image_count < 1 or image_count > 4:
        raise LayoutOverflowError(
            prefixed_message(f"vertical_stack requires 1 to 4 images, got {image_count}.")
        )

    labels = _normalized_label_heights(label_heights, image_count)
    base_metrics = metrics or VerticalStackMetrics(footer_height=footer_height)
    scaled = _scale_metrics(base_metrics, canvas_size.width)
    footer = scaled.footer_height if reserve_footer else 0

    normal = _try_layout(
        canvas_size,
        image_count=image_count,
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        outer_margin=scaled.outer_margin,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.title_gap,
        block_gap=scaled.block_gap,
        image_label_gap=scaled.image_label_gap,
        label_after_gap=scaled.label_after_gap,
    )
    if normal is not None:
        return normal

    reduced = _try_layout(
        canvas_size,
        image_count=image_count,
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        outer_margin=scaled.outer_margin,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.min_title_gap,
        block_gap=scaled.min_block_gap,
        image_label_gap=scaled.min_image_label_gap,
        label_after_gap=scaled.min_label_after_gap,
    )
    if reduced is not None:
        return reduced

    required = _required_non_image_space(
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.min_title_gap,
        block_gap=scaled.min_block_gap,
        image_label_gap=scaled.min_image_label_gap,
        label_after_gap=scaled.min_label_after_gap,
    )
    raise LayoutOverflowError(
        prefixed_message(
            "vertical_stack overflow: "
            f"canvas={canvas_size.width}x{canvas_size.height}; "
            f"images={image_count}; title_height={title_height}; "
            f"label_heights={labels}; required_non_image={required}; "
            f"available={canvas_size.height}."
        )
    )


def calculate_grid_2x2(
    canvas_size: CanvasSize,
    *,
    image_count: int,
    title_height: int = 0,
    label_heights: tuple[int, ...] = (),
    reserve_footer: bool = False,
    footer_height: int = 0,
    metrics: GridMetrics | None = None,
) -> SlideLayout:
    if image_count < 1 or image_count > 4:
        raise LayoutOverflowError(
            prefixed_message(f"grid_2x2 requires 1 to 4 images, got {image_count}.")
        )

    labels = _normalized_label_heights(label_heights, image_count)
    rows = _grid_rows(image_count)
    base_metrics = metrics or GridMetrics(footer_height=footer_height)
    scaled = _scale_grid_metrics(base_metrics, canvas_size.width)
    footer = scaled.footer_height if reserve_footer else 0

    normal = _try_grid_layout(
        canvas_size,
        rows=rows,
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        outer_margin=scaled.outer_margin,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.title_gap,
        row_gap=scaled.row_gap,
        column_gap=scaled.column_gap,
        image_label_gap=scaled.image_label_gap,
        label_after_gap=scaled.label_after_gap,
    )
    if normal is not None:
        return normal

    reduced = _try_grid_layout(
        canvas_size,
        rows=rows,
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        outer_margin=scaled.outer_margin,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.min_title_gap,
        row_gap=scaled.min_row_gap,
        column_gap=scaled.min_column_gap,
        image_label_gap=scaled.min_image_label_gap,
        label_after_gap=scaled.min_label_after_gap,
    )
    if reduced is not None:
        return reduced

    required = _required_grid_non_image_space(
        rows=rows,
        title_height=title_height,
        label_heights=labels,
        reserve_footer=reserve_footer,
        footer_height=footer,
        top_margin=scaled.top_margin,
        bottom_margin=scaled.bottom_margin,
        title_gap=scaled.min_title_gap,
        row_gap=scaled.min_row_gap,
        image_label_gap=scaled.min_image_label_gap,
        label_after_gap=scaled.min_label_after_gap,
    )
    raise LayoutOverflowError(
        prefixed_message(
            "grid_2x2 overflow: "
            f"canvas={canvas_size.width}x{canvas_size.height}; "
            f"layout=grid_2x2; images={image_count}; title_height={title_height}; "
            f"label_heights={labels}; required_non_image={required}; "
            f"available={canvas_size.height}."
        )
    )


def _normalized_label_heights(label_heights: tuple[int, ...], image_count: int) -> tuple[int, ...]:
    padded = tuple(max(0, height) for height in label_heights[:image_count])
    if len(padded) < image_count:
        padded = padded + tuple(0 for _ in range(image_count - len(padded)))
    return padded


def _scale_metrics(metrics: VerticalStackMetrics, canvas_width: int) -> VerticalStackMetrics:
    scale = canvas_width / BASE_CANVAS_WIDTH
    return VerticalStackMetrics(
        outer_margin=_scaled(metrics.outer_margin, scale),
        top_margin=_scaled(metrics.top_margin, scale),
        bottom_margin=_scaled(metrics.bottom_margin, scale),
        title_gap=_scaled(metrics.title_gap, scale),
        block_gap=_scaled(metrics.block_gap, scale),
        image_label_gap=_scaled(metrics.image_label_gap, scale),
        label_after_gap=_scaled(metrics.label_after_gap, scale),
        footer_height=_scaled(metrics.footer_height, scale),
        min_title_gap=_scaled(metrics.min_title_gap, scale),
        min_block_gap=_scaled(metrics.min_block_gap, scale),
        min_image_label_gap=_scaled(metrics.min_image_label_gap, scale),
        min_label_after_gap=_scaled(metrics.min_label_after_gap, scale),
    )


def _scale_grid_metrics(metrics: GridMetrics, canvas_width: int) -> GridMetrics:
    scale = canvas_width / BASE_CANVAS_WIDTH
    return GridMetrics(
        outer_margin=_scaled(metrics.outer_margin, scale),
        top_margin=_scaled(metrics.top_margin, scale),
        bottom_margin=_scaled(metrics.bottom_margin, scale),
        title_gap=_scaled(metrics.title_gap, scale),
        row_gap=_scaled(metrics.row_gap, scale),
        column_gap=_scaled(metrics.column_gap, scale),
        image_label_gap=_scaled(metrics.image_label_gap, scale),
        label_after_gap=_scaled(metrics.label_after_gap, scale),
        footer_height=_scaled(metrics.footer_height, scale),
        min_title_gap=_scaled(metrics.min_title_gap, scale),
        min_row_gap=_scaled(metrics.min_row_gap, scale),
        min_column_gap=_scaled(metrics.min_column_gap, scale),
        min_image_label_gap=_scaled(metrics.min_image_label_gap, scale),
        min_label_after_gap=_scaled(metrics.min_label_after_gap, scale),
    )


def _scaled(value: int, scale: float) -> int:
    return max(0, round(value * scale))


def _try_layout(
    canvas_size: CanvasSize,
    *,
    image_count: int,
    title_height: int,
    label_heights: tuple[int, ...],
    reserve_footer: bool,
    footer_height: int,
    outer_margin: int,
    top_margin: int,
    bottom_margin: int,
    title_gap: int,
    block_gap: int,
    image_label_gap: int,
    label_after_gap: int,
) -> SlideLayout | None:
    content_width = canvas_size.width - (2 * outer_margin)
    if content_width < 1:
        return None

    label_count = sum(1 for height in label_heights if height > 0)
    labeled_followed_count = sum(
        1 for index, height in enumerate(label_heights[:-1]) if height > 0
    )
    unlabeled_followed_count = sum(
        1 for index, height in enumerate(label_heights[:-1]) if height == 0
    )
    total_gap = (
        (block_gap * unlabeled_followed_count)
        + (image_label_gap * label_count)
        + (label_after_gap * labeled_followed_count)
    )
    if title_height > 0:
        total_gap += title_gap
    footer = footer_height if reserve_footer else 0
    non_image = top_margin + bottom_margin + footer + title_height + sum(label_heights) + total_gap
    image_space = canvas_size.height - non_image
    if image_space < image_count:
        return None

    image_heights = _distribute(image_space, image_count)
    y = top_margin
    title_rect = None
    if title_height > 0:
        title_rect = Rect(outer_margin, y, content_width, title_height)
        y += title_height + title_gap

    blocks: list[BlockLayout] = []
    for index, image_height in enumerate(image_heights):
        image_rect = Rect(outer_margin, y, content_width, image_height)
        y += image_height
        label_rect = None
        label_height = label_heights[index]
        if label_height > 0:
            y += image_label_gap
            label_rect = Rect(outer_margin, y, content_width, label_height)
            y += label_height
        if index < image_count - 1:
            y += label_after_gap if label_height > 0 else block_gap
        blocks.append(BlockLayout(image_rect, label_rect))

    footer_rect = None
    if reserve_footer and footer > 0:
        footer_rect = Rect(
            outer_margin,
            canvas_size.height - bottom_margin - footer,
            content_width,
            footer,
        )
    return SlideLayout(title_rect, tuple(blocks), footer_rect)


def _try_grid_layout(
    canvas_size: CanvasSize,
    *,
    rows: tuple[tuple[int, ...], ...],
    title_height: int,
    label_heights: tuple[int, ...],
    reserve_footer: bool,
    footer_height: int,
    outer_margin: int,
    top_margin: int,
    bottom_margin: int,
    title_gap: int,
    row_gap: int,
    column_gap: int,
    image_label_gap: int,
    label_after_gap: int,
) -> SlideLayout | None:
    content_width = canvas_size.width - (2 * outer_margin)
    if content_width < 1:
        return None
    if any(len(row) == 2 and content_width - column_gap < 2 for row in rows):
        return None

    row_label_heights = tuple(max(label_heights[index] for index in row) for row in rows)
    labeled_row_count = sum(1 for height in row_label_heights if height > 0)
    followed_labeled_row_count = sum(1 for height in row_label_heights[:-1] if height > 0)
    followed_unlabeled_row_count = sum(1 for height in row_label_heights[:-1] if height == 0)
    footer = footer_height if reserve_footer else 0
    total_gap = (
        (row_gap * followed_unlabeled_row_count)
        + (label_after_gap * followed_labeled_row_count)
        + (image_label_gap * labeled_row_count)
    )
    if title_height > 0:
        total_gap += title_gap
    non_image = (
        top_margin
        + bottom_margin
        + footer
        + title_height
        + sum(row_label_heights)
        + total_gap
    )
    image_space = canvas_size.height - non_image
    if image_space < len(rows):
        return None

    row_image_heights = _distribute(image_space, len(rows))
    y = top_margin
    title_rect = None
    if title_height > 0:
        title_rect = Rect(outer_margin, y, content_width, title_height)
        y += title_height + title_gap

    blocks_by_index: dict[int, BlockLayout] = {}
    for row_index, row in enumerate(rows):
        image_height = row_image_heights[row_index]
        columns = _grid_columns(content_width, column_gap, len(row))
        for index, x_offset, width in columns:
            item_index = row[index]
            image_rect = Rect(outer_margin + x_offset, y, width, image_height)
            label_rect = None
            if label_heights[item_index] > 0:
                label_rect = Rect(
                    outer_margin + x_offset,
                    y + image_height + image_label_gap,
                    width,
                    row_label_heights[row_index],
                )
            blocks_by_index[item_index] = BlockLayout(image_rect, label_rect)

        y += image_height
        if row_label_heights[row_index] > 0:
            y += image_label_gap + row_label_heights[row_index]
        if row_index < len(rows) - 1:
            y += label_after_gap if row_label_heights[row_index] > 0 else row_gap

    footer_rect = None
    if reserve_footer and footer > 0:
        footer_rect = Rect(
            outer_margin,
            canvas_size.height - bottom_margin - footer,
            content_width,
            footer,
        )
    blocks = tuple(blocks_by_index[index] for index in range(sum(len(row) for row in rows)))
    return SlideLayout(title_rect, blocks, footer_rect)


def _grid_rows(image_count: int) -> tuple[tuple[int, ...], ...]:
    if image_count == 1:
        return ((0,),)
    if image_count == 2:
        return ((0, 1),)
    if image_count == 3:
        return ((0,), (1, 2))
    return ((0, 1), (2, 3))


def _grid_columns(
    content_width: int,
    column_gap: int,
    count: int,
) -> tuple[tuple[int, int, int], ...]:
    if count == 1:
        return ((0, 0, content_width),)
    left_width = (content_width - column_gap) // 2
    right_width = content_width - column_gap - left_width
    return ((0, 0, left_width), (1, left_width + column_gap, right_width))


def _distribute(total: int, count: int) -> tuple[int, ...]:
    base = total // count
    remainder = total % count
    return tuple(base + (1 if index < remainder else 0) for index in range(count))


def _required_non_image_space(
    *,
    title_height: int,
    label_heights: tuple[int, ...],
    reserve_footer: bool,
    footer_height: int,
    top_margin: int,
    bottom_margin: int,
    title_gap: int,
    block_gap: int,
    image_label_gap: int,
    label_after_gap: int,
) -> int:
    label_count = sum(1 for height in label_heights if height > 0)
    labeled_followed_count = sum(1 for height in label_heights[:-1] if height > 0)
    unlabeled_followed_count = sum(1 for height in label_heights[:-1] if height == 0)
    return (
        top_margin
        + bottom_margin
        + (footer_height if reserve_footer else 0)
        + title_height
        + sum(label_heights)
        + (title_gap if title_height > 0 else 0)
        + (block_gap * unlabeled_followed_count)
        + (image_label_gap * label_count)
        + (label_after_gap * labeled_followed_count)
    )


def _required_grid_non_image_space(
    *,
    rows: tuple[tuple[int, ...], ...],
    title_height: int,
    label_heights: tuple[int, ...],
    reserve_footer: bool,
    footer_height: int,
    top_margin: int,
    bottom_margin: int,
    title_gap: int,
    row_gap: int,
    image_label_gap: int,
    label_after_gap: int,
) -> int:
    row_label_heights = tuple(max(label_heights[index] for index in row) for row in rows)
    labeled_row_count = sum(1 for height in row_label_heights if height > 0)
    followed_labeled_row_count = sum(1 for height in row_label_heights[:-1] if height > 0)
    followed_unlabeled_row_count = sum(1 for height in row_label_heights[:-1] if height == 0)
    return (
        top_margin
        + bottom_margin
        + (footer_height if reserve_footer else 0)
        + title_height
        + sum(row_label_heights)
        + (title_gap if title_height > 0 else 0)
        + (row_gap * followed_unlabeled_row_count)
        + (image_label_gap * labeled_row_count)
        + (label_after_gap * followed_labeled_row_count)
    )
