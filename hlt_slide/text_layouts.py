"""Pure geometry engine for the future HLT Text Composer node."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from .config import CanvasSize, Rect


BASE_CANVAS_WIDTH = 1080.0
TEXT_LAYOUT_NAMES = (
    "auto_text",
    "centered_statement",
    "vertical_stack",
    "split_2",
    "grid_2x2",
    "editorial_quote",
)
TEXT_ROLES = (
    "headline",
    "subheadline",
    "body",
    "quote",
    "caption",
    "number",
    "label",
)
DEFAULT_TEXT_ROLES = ("headline", "headline", "headline", "headline")
ROLE_GEOMETRY_WEIGHTS: Mapping[str, float] = MappingProxyType(
    {
        "number": 1.50,
        "headline": 1.35,
        "quote": 1.25,
        "subheadline": 1.00,
        "body": 0.90,
        "label": 0.70,
        "caption": 0.60,
    }
)


@dataclass(frozen=True)
class TextSourceBlock:
    source_index: int
    text: str
    role: str

    @property
    def is_active(self) -> bool:
        return bool(self.text.strip())


@dataclass(frozen=True)
class TextLayoutSettings:
    outer_margin: int = 64
    top_margin: int = 60
    bottom_margin: int = 54
    block_gap: int = 30
    inner_padding: int = 30
    minimum_block_width: int = 24
    minimum_block_height: int = 24
    split_axis: str = "auto"

    def __post_init__(self) -> None:
        for name in (
            "outer_margin",
            "top_margin",
            "bottom_margin",
            "block_gap",
            "inner_padding",
            "minimum_block_width",
            "minimum_block_height",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative.")
        if self.split_axis not in {"auto", "horizontal", "vertical"}:
            raise ValueError("split_axis must be 'auto', 'horizontal' or 'vertical'.")


@dataclass(frozen=True)
class TextBlockLayout:
    source_index: int
    role: str
    rect: Rect
    inner_rect: Rect
    weight: float
    grid_cell: tuple[int, int] | None = None


@dataclass(frozen=True)
class TextLayoutDiagnostics:
    requested_layout: str
    effective_layout: str
    active_count: int
    source_order: tuple[int, ...]
    roles: tuple[str, ...]
    split_axis_resolved: str | None
    content_usage_percentage: float


@dataclass(frozen=True)
class TextCompositionLayout:
    requested_layout: str
    effective_layout: str
    blocks: tuple[TextBlockLayout, ...]
    content_rect: Rect
    diagnostics: TextLayoutDiagnostics


def active_text_blocks(
    text_slots: Sequence[str],
    role_slots: Sequence[str] | None = None,
) -> tuple[TextSourceBlock, ...]:
    if len(text_slots) > 4:
        raise ValueError(f"Text Composer supports at most 4 text slots, got {len(text_slots)}.")
    roles = _role_slots(role_slots, len(text_slots))
    blocks = []
    for source_index, text in enumerate(text_slots):
        role = roles[source_index]
        _validate_role(role)
        if not str(text).strip():
            continue
        blocks.append(TextSourceBlock(source_index=source_index, text=str(text), role=role))
    if not blocks:
        raise ValueError("Text Composer requires at least one active text block.")
    return tuple(blocks)


def resolve_text_layout_name(requested_layout: str, active_count: int) -> str:
    if active_count < 1 or active_count > 4:
        raise ValueError(f"Text layouts require 1 to 4 active blocks, got {active_count}.")
    if requested_layout == "auto_text":
        return {
            1: "centered_statement",
            2: "split_2",
            3: "vertical_stack",
            4: "grid_2x2",
        }[active_count]
    if requested_layout not in TEXT_LAYOUT_NAMES:
        raise ValueError(f"Unsupported text layout: {requested_layout!r}.")
    return requested_layout


def select_text_layout(
    canvas_size: CanvasSize,
    source_blocks: Sequence[TextSourceBlock],
    settings: TextLayoutSettings | None = None,
    requested_layout: str = "auto_text",
) -> TextCompositionLayout:
    blocks = tuple(source_blocks)
    _validate_source_blocks(blocks)
    layout_settings = settings or TextLayoutSettings()
    effective_layout = resolve_text_layout_name(requested_layout, len(blocks))
    content_rect = _content_rect(canvas_size, layout_settings)

    if effective_layout == "centered_statement":
        block_layouts, split_axis = _centered_statement(blocks, content_rect, layout_settings)
    elif effective_layout == "vertical_stack":
        block_layouts, split_axis = _vertical_stack(blocks, content_rect, layout_settings)
    elif effective_layout == "split_2":
        block_layouts, split_axis = _split_2(canvas_size, blocks, content_rect, layout_settings)
    elif effective_layout == "grid_2x2":
        block_layouts, split_axis = _grid_2x2(blocks, content_rect, layout_settings)
    elif effective_layout == "editorial_quote":
        block_layouts, split_axis = _editorial_quote(blocks, content_rect, layout_settings)
    else:
        raise ValueError(f"Unsupported text layout: {effective_layout!r}.")

    diagnostics = TextLayoutDiagnostics(
        requested_layout=requested_layout,
        effective_layout=effective_layout,
        active_count=len(blocks),
        source_order=tuple(block.source_index for block in blocks),
        roles=tuple(block.role for block in blocks),
        split_axis_resolved=split_axis,
        content_usage_percentage=_content_usage(content_rect, block_layouts),
    )
    return TextCompositionLayout(
        requested_layout=requested_layout,
        effective_layout=effective_layout,
        blocks=block_layouts,
        content_rect=content_rect,
        diagnostics=diagnostics,
    )


def describe_text_layout(layout: TextCompositionLayout) -> str:
    diagnostics = layout.diagnostics
    return (
        f"requested_layout={diagnostics.requested_layout}; "
        f"effective_layout={diagnostics.effective_layout}; "
        f"active_count={diagnostics.active_count}; "
        f"source_order={diagnostics.source_order}; "
        f"roles={diagnostics.roles}; "
        f"split_axis_resolved={diagnostics.split_axis_resolved}; "
        f"content_usage_percentage={diagnostics.content_usage_percentage:.2f}"
    )


def _role_slots(role_slots: Sequence[str] | None, count: int) -> tuple[str, ...]:
    if role_slots is None:
        return DEFAULT_TEXT_ROLES[:count]
    if len(role_slots) < count:
        return tuple(role_slots) + DEFAULT_TEXT_ROLES[len(role_slots) : count]
    return tuple(role_slots[:count])


def _validate_role(role: str) -> None:
    if role not in TEXT_ROLES:
        raise ValueError(f"Invalid text role: {role!r}.")


def _validate_source_blocks(blocks: tuple[TextSourceBlock, ...]) -> None:
    if len(blocks) < 1 or len(blocks) > 4:
        raise ValueError(f"Text layouts require 1 to 4 active blocks, got {len(blocks)}.")
    for block in blocks:
        _validate_role(block.role)
        if not block.is_active:
            raise ValueError("source_blocks must contain only active text blocks.")


def _content_rect(canvas_size: CanvasSize, settings: TextLayoutSettings) -> Rect:
    scale = canvas_size.width / BASE_CANVAS_WIDTH
    outer_margin = _scaled(settings.outer_margin, scale)
    top_margin = _scaled(settings.top_margin, scale)
    bottom_margin = _scaled(settings.bottom_margin, scale)
    width = canvas_size.width - (2 * outer_margin)
    height = canvas_size.height - top_margin - bottom_margin
    if width < settings.minimum_block_width or height < settings.minimum_block_height:
        raise ValueError(
            "Canvas and margins leave no positive text content area "
            f"({width}x{height})."
        )
    return Rect(outer_margin, top_margin, width, height)


def _centered_statement(
    blocks: tuple[TextSourceBlock, ...],
    content_rect: Rect,
    settings: TextLayoutSettings,
) -> tuple[tuple[TextBlockLayout, ...], None]:
    if len(blocks) != 1:
        raise ValueError("centered_statement requires exactly 1 active block.")
    width = max(settings.minimum_block_width, round(content_rect.width * 0.8865))
    height = max(settings.minimum_block_height, round(content_rect.height * 0.4651))
    width = min(width, content_rect.width)
    height = min(height, content_rect.height)
    rect = Rect(
        content_rect.x + ((content_rect.width - width) // 2),
        max(content_rect.y, (content_rect.y + content_rect.bottom - height) // 2 - 3),
        width,
        height,
    )
    return (_layout_blocks(blocks, (rect,), settings), None)


def _vertical_stack(
    blocks: tuple[TextSourceBlock, ...],
    content_rect: Rect,
    settings: TextLayoutSettings,
) -> tuple[tuple[TextBlockLayout, ...], None]:
    if len(blocks) > 4:
        raise ValueError("vertical_stack supports 1 to 4 active blocks.")
    gap = _usable_gap(settings.block_gap, len(blocks), content_rect.height)
    available_height = content_rect.height - (gap * (len(blocks) - 1))
    heights = _weighted_sizes(
        available_height,
        tuple(_role_weight(block.role) for block in blocks),
        settings.minimum_block_height,
    )
    rects = []
    y = content_rect.y
    for height in heights:
        rects.append(Rect(content_rect.x, y, content_rect.width, height))
        y += height + gap
    return (_layout_blocks(blocks, tuple(rects), settings), None)


def _split_2(
    canvas_size: CanvasSize,
    blocks: tuple[TextSourceBlock, ...],
    content_rect: Rect,
    settings: TextLayoutSettings,
) -> tuple[tuple[TextBlockLayout, ...], str]:
    if len(blocks) != 2:
        raise ValueError("split_2 requires exactly 2 active blocks.")
    axis = _resolved_split_axis(canvas_size, settings)
    gap = _usable_gap(
        settings.block_gap,
        2,
        content_rect.width if axis == "horizontal" else content_rect.height,
    )
    if axis == "horizontal":
        widths = _distribute(content_rect.width - gap, 2)
        rects = (
            Rect(content_rect.x, content_rect.y, widths[0], content_rect.height),
            Rect(content_rect.x + widths[0] + gap, content_rect.y, widths[1], content_rect.height),
        )
    else:
        heights = _distribute(content_rect.height - gap, 2)
        rects = (
            Rect(content_rect.x, content_rect.y, content_rect.width, heights[0]),
            Rect(content_rect.x, content_rect.y + heights[0] + gap, content_rect.width, heights[1]),
        )
    return (_layout_blocks(blocks, rects, settings), axis)


def _grid_2x2(
    blocks: tuple[TextSourceBlock, ...],
    content_rect: Rect,
    settings: TextLayoutSettings,
) -> tuple[tuple[TextBlockLayout, ...], None]:
    if len(blocks) < 2 or len(blocks) > 4:
        raise ValueError("grid_2x2 requires 2 to 4 active blocks.")
    gap = _usable_gap(settings.block_gap, 2, min(content_rect.width, content_rect.height))
    widths = _distribute(content_rect.width - gap, 2)
    heights = _distribute(content_rect.height - gap, 2)
    cells = (
        Rect(content_rect.x, content_rect.y, widths[0], heights[0]),
        Rect(content_rect.x + widths[0] + gap, content_rect.y, widths[1], heights[0]),
        Rect(content_rect.x, content_rect.y + heights[0] + gap, widths[0], heights[1]),
        Rect(content_rect.x + widths[0] + gap, content_rect.y + heights[0] + gap, widths[1], heights[1]),
    )
    cell_positions = ((0, 0), (0, 1), (1, 0), (1, 1))
    layouts = _layout_blocks(blocks, cells[: len(blocks)], settings, cell_positions)
    return (layouts, None)


def _editorial_quote(
    blocks: tuple[TextSourceBlock, ...],
    content_rect: Rect,
    settings: TextLayoutSettings,
) -> tuple[tuple[TextBlockLayout, ...], None]:
    if len(blocks) < 1 or len(blocks) > 2:
        raise ValueError("editorial_quote requires 1 or 2 active blocks.")
    if len(blocks) == 1:
        return (_layout_blocks(blocks, (content_rect,), settings), None)
    gap = _usable_gap(settings.block_gap, 2, content_rect.height)
    main_height = round((content_rect.height - gap) * 0.78)
    secondary_height = content_rect.height - gap - main_height
    if secondary_height < settings.minimum_block_height:
        secondary_height = settings.minimum_block_height
        main_height = content_rect.height - gap - secondary_height
    rects = (
        Rect(content_rect.x, content_rect.y, content_rect.width, main_height),
        Rect(content_rect.x, content_rect.y + main_height + gap, content_rect.width, secondary_height),
    )
    return (_layout_blocks(blocks, rects, settings), None)


def _layout_blocks(
    blocks: tuple[TextSourceBlock, ...],
    rects: tuple[Rect, ...],
    settings: TextLayoutSettings,
    grid_cells: tuple[tuple[int, int], ...] | None = None,
) -> tuple[TextBlockLayout, ...]:
    layouts = []
    for index, (block, rect) in enumerate(zip(blocks, rects)):
        inner = _inner_rect(rect, settings.inner_padding)
        layouts.append(
            TextBlockLayout(
                source_index=block.source_index,
                role=block.role,
                rect=rect,
                inner_rect=inner,
                weight=_role_weight(block.role),
                grid_cell=grid_cells[index] if grid_cells is not None else None,
            )
        )
    return tuple(layouts)


def _inner_rect(rect: Rect, padding: int) -> Rect:
    padding = min(padding, max(0, (rect.width - 1) // 2), max(0, (rect.height - 1) // 2))
    return Rect(
        rect.x + padding,
        rect.y + padding,
        max(1, rect.width - (2 * padding)),
        max(1, rect.height - (2 * padding)),
    )


def _resolved_split_axis(canvas_size: CanvasSize, settings: TextLayoutSettings) -> str:
    if settings.split_axis in {"horizontal", "vertical"}:
        return settings.split_axis
    if canvas_size.width > canvas_size.height:
        return "horizontal"
    return "vertical"


def _role_weight(role: str) -> float:
    return ROLE_GEOMETRY_WEIGHTS[role]


def _content_usage(content_rect: Rect, blocks: tuple[TextBlockLayout, ...]) -> float:
    content_area = content_rect.width * content_rect.height
    if content_area <= 0:
        return 0.0
    block_area = sum(block.rect.width * block.rect.height for block in blocks)
    return round(min(100.0, 100.0 * block_area / content_area), 6)


def _scaled(value: int, scale: float) -> int:
    return max(0, round(value * scale))


def _usable_gap(requested_gap: int, count: int, available: int) -> int:
    if count <= 1:
        return 0
    max_gap = max(0, (available - count) // (count - 1))
    return min(requested_gap, max_gap)


def _weighted_sizes(total: int, weights: tuple[float, ...], minimum: int) -> tuple[int, ...]:
    if total < minimum * len(weights):
        raise ValueError("Text layout cannot satisfy minimum block heights.")
    remaining = total - (minimum * len(weights))
    weight_sum = sum(weights)
    raw = [remaining * (weight / weight_sum) for weight in weights]
    extras = _rounded_parts(raw, remaining)
    return tuple(minimum + extra for extra in extras)


def _rounded_parts(raw_parts: Sequence[float], target_total: int) -> tuple[int, ...]:
    parts = [int(value) for value in raw_parts]
    fractions = sorted(
        ((raw_parts[index] - parts[index], index) for index in range(len(parts))),
        key=lambda item: (-item[0], item[1]),
    )
    while sum(parts) < target_total:
        for _fraction, index in fractions:
            if sum(parts) >= target_total:
                break
            parts[index] += 1
    while sum(parts) > target_total:
        for _fraction, index in reversed(fractions):
            if sum(parts) <= target_total:
                break
            if parts[index] > 0:
                parts[index] -= 1
    return tuple(parts)


def _distribute(total: int, count: int) -> tuple[int, ...]:
    if total < count:
        raise ValueError("Cannot distribute fewer pixels than slots.")
    base = total // count
    remainder = total % count
    return tuple(base + (1 if index < remainder else 0) for index in range(count))
