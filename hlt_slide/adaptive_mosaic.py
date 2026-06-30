"""Pure geometry engine for experimental adaptive mosaic layouts."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Sequence

from .config import CanvasSize, Rect
from .layouts import BlockLayout, SlideLayout


PENALTY_KEYS = (
    "unused_area",
    "tiny_cells",
    "aspect_error",
    "visual_imbalance",
    "extreme_size_difference",
    "label_overflow",
    "order_change",
    "edge_misalignment",
)

STRATEGY_WEIGHTS: Mapping[str, Mapping[str, float]] = {
    "balanced": MappingProxyType(
        {
            "unused_area": 1.25,
            "tiny_cells": 3.0,
            "aspect_error": 60.0,
            "visual_imbalance": 1.4,
            "extreme_size_difference": 1.2,
            "label_overflow": 1.0,
            "order_change": 1.0,
            "edge_misalignment": 0.8,
        }
    ),
    "editorial": MappingProxyType(
        {
            "unused_area": 0.85,
            "tiny_cells": 2.0,
            "aspect_error": 60.0,
            "visual_imbalance": 0.35,
            "extreme_size_difference": 0.45,
            "label_overflow": 1.0,
            "order_change": 1.0,
            "edge_misalignment": 0.7,
        }
    ),
    "compact": MappingProxyType(
        {
            "unused_area": 2.4,
            "tiny_cells": 3.2,
            "aspect_error": 60.0,
            "visual_imbalance": 1.0,
            "extreme_size_difference": 0.9,
            "label_overflow": 1.0,
            "order_change": 1.0,
            "edge_misalignment": 0.8,
        }
    ),
}

INVALID_PENALTY = 10_000.0
LABEL_OVERFLOW_PENALTY = 1_000.0
ORDER_CHANGE_PENALTY = 120.0
MINIMUM_AREA_SCORE = 0.01
DEFAULT_LABEL_HEIGHT = 48
DEFAULT_FOOTER_GAP = 24


@dataclass(frozen=True)
class SourceImageInfo:
    index: int
    width: int
    height: int
    aspect_ratio: float
    has_label: bool

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("Source image width and height must be positive.")
        if self.aspect_ratio <= 0:
            raise ValueError("Source image aspect_ratio must be positive.")


@dataclass(frozen=True)
class AdaptiveMosaicSettings:
    strategy: str = "balanced"
    preserve_order: bool = True
    preserve_aspect: bool = True
    hero_index: int | None = None
    gap: int = 24
    minimum_image_width: int = 96
    minimum_image_height: int = 96
    label_padding_top: int = 8
    label_padding_bottom: int = 8
    label_after_gap: int = 16
    label_min_height: int = DEFAULT_LABEL_HEIGHT
    footer_height: int = 0
    footer_gap: int = DEFAULT_FOOTER_GAP

    def __post_init__(self) -> None:
        if self.strategy not in STRATEGY_WEIGHTS:
            raise ValueError(f"Unknown adaptive mosaic strategy: {self.strategy!r}.")
        numeric_fields = {
            "gap": self.gap,
            "minimum_image_width": self.minimum_image_width,
            "minimum_image_height": self.minimum_image_height,
            "label_padding_top": self.label_padding_top,
            "label_padding_bottom": self.label_padding_bottom,
            "label_after_gap": self.label_after_gap,
            "label_min_height": self.label_min_height,
            "footer_height": self.footer_height,
            "footer_gap": self.footer_gap,
        }
        for name, value in numeric_fields.items():
            if value < 0:
                raise ValueError(f"Adaptive mosaic setting {name} must not be negative.")


@dataclass(frozen=True)
class MosaicCandidate:
    template_name: str
    blocks: tuple[BlockLayout, ...]
    score: float
    penalties: Mapping[str, float]
    diagnostics: Mapping[str, object] = field(default_factory=dict)
    source_order: tuple[int, ...] = ()


@dataclass(frozen=True)
class _Template:
    name: str
    kind: str
    groups: tuple[tuple[int, ...], ...]
    hero_position: str | None = None


def select_adaptive_mosaic(
    canvas_size: CanvasSize,
    sources: Sequence[SourceImageInfo],
    settings: AdaptiveMosaicSettings | None = None,
    *,
    content_rect: Rect | None = None,
    title_rect: Rect | None = None,
    footer_rect: Rect | None = None,
    label_heights: Sequence[int] = (),
) -> tuple[SlideLayout, MosaicCandidate]:
    mosaic_settings = settings or AdaptiveMosaicSettings()
    candidates = generate_mosaic_candidates(
        canvas_size,
        sources,
        mosaic_settings,
        content_rect=content_rect,
        footer_rect=footer_rect,
        label_heights=label_heights,
    )
    if not candidates:
        raise ValueError("adaptive_mosaic requires at least one valid candidate.")
    winner = max(candidates, key=lambda candidate: (candidate.score, -_template_rank(candidate)))
    return (
        _slide_from_candidate(canvas_size, winner, mosaic_settings, title_rect, footer_rect),
        winner,
    )


def generate_mosaic_candidates(
    canvas_size: CanvasSize,
    sources: Sequence[SourceImageInfo],
    settings: AdaptiveMosaicSettings | None = None,
    *,
    content_rect: Rect | None = None,
    footer_rect: Rect | None = None,
    label_heights: Sequence[int] = (),
) -> tuple[MosaicCandidate, ...]:
    mosaic_settings = settings or AdaptiveMosaicSettings()
    source_tuple = _validate_sources(sources)
    labels = _resolved_label_heights(source_tuple, label_heights, mosaic_settings)
    content_rect, footer_rect = _resolved_content_and_footer_rect(
        canvas_size, mosaic_settings, content_rect, footer_rect
    )
    candidates: list[MosaicCandidate] = []
    for template in _templates_for_count(len(source_tuple), mosaic_settings):
        blocks = _blocks_for_template(
            template,
            source_tuple,
            labels,
            content_rect,
            mosaic_settings,
        )
        if blocks is None:
            continue
        ordered_blocks = _blocks_in_source_order(blocks, len(source_tuple))
        raw_candidate = MosaicCandidate(
            template_name=template.name,
            blocks=ordered_blocks,
            score=0.0,
            penalties=MappingProxyType({key: 0.0 for key in PENALTY_KEYS}),
            diagnostics=MappingProxyType({}),
            source_order=tuple(item for group in template.groups for item in group),
        )
        scored = score_mosaic_candidate(
            raw_candidate,
            canvas_size,
            source_tuple,
            mosaic_settings,
            content_rect=content_rect,
            footer_rect=footer_rect,
        )
        candidates.append(scored)
    return tuple(sorted(candidates, key=lambda candidate: candidate.template_name))


def fit_rect_preserving_aspect(
    source_width: int,
    source_height: int,
    available_rect: Rect,
    alignment: tuple[str, str] = ("center", "center"),
) -> Rect:
    if source_width < 1 or source_height < 1:
        raise ValueError("source_width and source_height must be positive.")
    if available_rect.width < 1 or available_rect.height < 1:
        raise ValueError("available_rect must have positive dimensions.")

    source_ratio = source_width / source_height
    available_ratio = available_rect.width / available_rect.height
    if source_ratio >= available_ratio:
        width = available_rect.width
        height = max(1, round(width / source_ratio))
    else:
        height = available_rect.height
        width = max(1, round(height * source_ratio))

    x = _aligned_start(available_rect.x, available_rect.width, width, alignment[0])
    y = _aligned_start(available_rect.y, available_rect.height, height, alignment[1])
    return Rect(x, y, width, height)


def build_justified_rows(
    sources: Sequence[SourceImageInfo],
    row_groups: tuple[tuple[int, ...], ...],
    available_rect: Rect,
    *,
    gap: int,
    minimum_image_width: int = 1,
    minimum_image_height: int = 1,
) -> tuple[tuple[Rect, ...], ...]:
    source_tuple = tuple(sources)
    if available_rect.width < 1 or available_rect.height < 1:
        raise ValueError("available_rect must have positive dimensions.")
    if gap < 0:
        raise ValueError("gap must not be negative.")
    if not row_groups:
        raise ValueError("row_groups must not be empty.")

    raw_heights = tuple(
        _justified_row_height(source_tuple, row, available_rect.width, gap) for row in row_groups
    )
    total_raw_height = sum(raw_heights) + gap * (len(row_groups) - 1)
    if total_raw_height <= 0:
        raise ValueError("Unable to calculate justified row height.")
    scale = min(1.0, available_rect.height / total_raw_height)
    row_heights = _distribute_scaled(raw_heights, scale, available_rect.height, gap)

    y = available_rect.y
    rows: list[tuple[Rect, ...]] = []
    for row_index, (row, height) in enumerate(zip(row_groups, row_heights)):
        rects = _justified_row_rects(
            source_tuple,
            row,
            Rect(available_rect.x, y, available_rect.width, height),
            gap,
        )
        if any(
            rect.width < minimum_image_width or rect.height < minimum_image_height
            for rect in rects
        ):
            raise ValueError("Justified row cannot satisfy minimum image dimensions.")
        rows.append(rects)
        y += height + (gap if row_index < len(row_groups) - 1 else 0)
    return tuple(rows)


def score_mosaic_candidate(
    candidate: MosaicCandidate,
    canvas_size: CanvasSize,
    sources: Sequence[SourceImageInfo],
    settings: AdaptiveMosaicSettings | None = None,
    *,
    content_rect: Rect | None = None,
    footer_rect: Rect | None = None,
) -> MosaicCandidate:
    mosaic_settings = settings or AdaptiveMosaicSettings()
    source_tuple = _validate_sources(sources)
    content = content_rect or _content_and_footer_rect(canvas_size, mosaic_settings)[0]
    footer = footer_rect

    raw_penalties = {
        "unused_area": _unused_area_penalty(candidate, content),
        "tiny_cells": _tiny_cells_penalty(candidate, mosaic_settings),
        "aspect_error": _aspect_error_penalty(candidate, source_tuple),
        "visual_imbalance": _visual_imbalance_penalty(candidate, mosaic_settings),
        "extreme_size_difference": _size_difference_penalty(candidate),
        "label_overflow": _label_overflow_penalty(candidate, content, footer),
        "order_change": _order_change_penalty(candidate, mosaic_settings),
        "edge_misalignment": _edge_misalignment_penalty(candidate, content),
    }
    weights = STRATEGY_WEIGHTS[mosaic_settings.strategy]
    penalties = {
        key: round(raw_penalties[key] * weights[key], 6)
        for key in PENALTY_KEYS
    }
    weighted_total = sum(penalties.values())
    score = round(max(MINIMUM_AREA_SCORE, 10_000.0 - weighted_total), 6)
    diagnostics = _diagnostics(candidate, source_tuple, content)
    return MosaicCandidate(
        template_name=candidate.template_name,
        blocks=candidate.blocks,
        score=score,
        penalties=MappingProxyType(penalties),
        diagnostics=MappingProxyType(diagnostics),
        source_order=candidate.source_order,
    )


def describe_candidate(candidate: MosaicCandidate) -> str:
    diagnostics = candidate.diagnostics
    penalties = ", ".join(
        f"{key}={candidate.penalties[key]:.3f}" for key in PENALTY_KEYS
    )
    return (
        f"{candidate.template_name}: score={candidate.score:.3f}; "
        f"source_aspect_ratio={diagnostics.get('source_aspect_ratio')}; "
        f"output_aspect_ratio={diagnostics.get('output_aspect_ratio')}; "
        f"unused_area_percentage={diagnostics.get('unused_area_percentage')}; "
        f"penalties=({penalties})"
    )


def _validate_sources(sources: Sequence[SourceImageInfo]) -> tuple[SourceImageInfo, ...]:
    source_tuple = tuple(sources)
    if len(source_tuple) < 1 or len(source_tuple) > 4:
        raise ValueError(f"adaptive_mosaic requires 1 to 4 images, got {len(source_tuple)}.")
    return source_tuple


def _templates_for_count(
    count: int, settings: AdaptiveMosaicSettings
) -> tuple[_Template, ...]:
    if count == 1:
        return (_Template("single", "single", ((0,),)),)
    if count == 2:
        templates = (
            _Template("row_2", "rows", ((0, 1),)),
            _Template("column_2", "columns", ((0,), (1,))),
            _Template("hero_left", "hero_side", ((0,), (1,)), "left"),
            _Template("hero_right", "hero_side", ((1,), (0,)), "right"),
            _Template("hero_top", "hero_stack", ((0,), (1,)), "top"),
            _Template("hero_bottom", "hero_stack", ((1,), (0,)), "bottom"),
        )
    elif count == 3:
        templates = (
            _Template("row_3", "rows", ((0, 1, 2),)),
            _Template("column_3", "columns", ((0,), (1,), (2,))),
            _Template("hero_left_2_stack", "hero_side", ((0,), (1, 2)), "left"),
            _Template("hero_right_2_stack", "hero_side", ((1, 2), (0,)), "right"),
            _Template("hero_top_2_row", "hero_stack", ((0,), (1, 2)), "top"),
            _Template("hero_bottom_2_row", "hero_stack", ((1, 2), (0,)), "bottom"),
            _Template("justified_1_2", "justified", ((0,), (1, 2))),
            _Template("justified_2_1", "justified", ((0, 1), (2,))),
        )
    else:
        templates = (
            _Template("grid_2x2", "grid", ((0, 1), (2, 3))),
            _Template("hero_left_3_stack", "hero_side", ((0,), (1, 2, 3)), "left"),
            _Template("hero_right_3_stack", "hero_side", ((1, 2, 3), (0,)), "right"),
            _Template("hero_top_3_row", "hero_stack", ((0,), (1, 2, 3)), "top"),
            _Template("hero_bottom_3_row", "hero_stack", ((1, 2, 3), (0,)), "bottom"),
            _Template("justified_1_3", "justified", ((0,), (1, 2, 3))),
            _Template("justified_3_1", "justified", ((0, 1, 2), (3,))),
            _Template("justified_2_2", "justified", ((0, 1), (2, 3))),
        )

    if settings.hero_index is None or settings.hero_index == 0:
        return templates
    return tuple(_reindex_template(template, settings.hero_index, count) for template in templates)


def _reindex_template(template: _Template, hero_index: int, count: int) -> _Template:
    if hero_index < 0 or hero_index >= count:
        raise ValueError(f"hero_index must refer to one of the {count} images.")
    index_map = (hero_index,) + tuple(index for index in range(count) if index != hero_index)
    groups = tuple(tuple(index_map[index] for index in group) for group in template.groups)
    return _Template(template.name, template.kind, groups, template.hero_position)


def _blocks_for_template(
    template: _Template,
    sources: tuple[SourceImageInfo, ...],
    label_heights: tuple[int, ...],
    content_rect: Rect,
    settings: AdaptiveMosaicSettings,
) -> dict[int, BlockLayout] | None:
    try:
        if template.kind == "single":
            cell_groups = ((Rect(content_rect.x, content_rect.y, content_rect.width, content_rect.height),),)
        elif template.kind == "rows":
            cell_groups = (_partition_row(content_rect, len(template.groups[0]), settings.gap),)
        elif template.kind == "columns":
            cell_groups = tuple(
                (rect,) for rect in _partition_column(content_rect, len(template.groups), settings.gap)
            )
        elif template.kind == "grid":
            row_rects = _partition_column(content_rect, len(template.groups), settings.gap)
            cell_groups = tuple(
                _partition_row(row_rect, len(group), settings.gap)
                for row_rect, group in zip(row_rects, template.groups)
            )
        elif template.kind == "hero_side":
            cell_groups = _hero_side_cells(content_rect, template, settings.gap)
        elif template.kind == "hero_stack":
            cell_groups = _hero_stack_cells(content_rect, template, settings.gap)
        elif template.kind == "justified":
            cell_groups = build_justified_rows(
                sources,
                template.groups,
                content_rect,
                gap=settings.gap,
                minimum_image_width=1,
                minimum_image_height=1,
            )
        else:
            return None
    except ValueError:
        return None

    blocks: dict[int, BlockLayout] = {}
    for group, cells in zip(template.groups, cell_groups):
        for source_index, cell in zip(group, cells):
            block = _block_from_cell(
                sources[source_index],
                label_heights[source_index],
                cell,
                settings,
            )
            blocks[source_index] = block
    return blocks


def _block_from_cell(
    source: SourceImageInfo,
    label_height: int,
    cell: Rect,
    settings: AdaptiveMosaicSettings,
) -> BlockLayout:
    has_label = source.has_label and label_height > 0
    reserved_label_height = label_height if has_label else 0
    label_gap = settings.label_after_gap if has_label else 0
    image_available_height = cell.height - reserved_label_height - label_gap
    image_available = Rect(cell.x, cell.y, cell.width, max(0, image_available_height))
    if image_available.width < 1 or image_available.height < 1:
        image_rect = image_available
        label_rect = None
        if has_label:
            label_rect = Rect(
                cell.x,
                cell.bottom - reserved_label_height,
                cell.width,
                reserved_label_height,
            )
        return BlockLayout(image_rect=image_rect, label_rect=label_rect)
    if settings.preserve_aspect:
        image_rect = fit_rect_preserving_aspect(
            source.width,
            source.height,
            image_available,
            alignment=("center", "center"),
        )
    else:
        image_rect = image_available

    label_rect = None
    if has_label:
        label_rect = Rect(
            cell.x,
            cell.bottom - reserved_label_height,
            cell.width,
            reserved_label_height,
        )
    return BlockLayout(image_rect=image_rect, label_rect=label_rect)


def _partition_row(rect: Rect, count: int, gap: int) -> tuple[Rect, ...]:
    total_gap = gap * (count - 1)
    widths = _distribute(rect.width - total_gap, count)
    x = rect.x
    cells = []
    for index, width in enumerate(widths):
        cells.append(Rect(x, rect.y, width, rect.height))
        x += width + (gap if index < count - 1 else 0)
    return tuple(cells)


def _partition_column(rect: Rect, count: int, gap: int) -> tuple[Rect, ...]:
    total_gap = gap * (count - 1)
    heights = _distribute(rect.height - total_gap, count)
    y = rect.y
    cells = []
    for index, height in enumerate(heights):
        cells.append(Rect(rect.x, y, rect.width, height))
        y += height + (gap if index < count - 1 else 0)
    return tuple(cells)


def _hero_side_cells(rect: Rect, template: _Template, gap: int) -> tuple[tuple[Rect, ...], ...]:
    hero_width = round(rect.width * 0.58)
    side_width = rect.width - hero_width - gap
    if template.hero_position == "right":
        stack_rect = Rect(rect.x, rect.y, side_width, rect.height)
        hero_rect = Rect(stack_rect.right + gap, rect.y, hero_width, rect.height)
        return (_partition_column(stack_rect, len(template.groups[0]), gap), (hero_rect,))
    hero_rect = Rect(rect.x, rect.y, hero_width, rect.height)
    stack_rect = Rect(hero_rect.right + gap, rect.y, side_width, rect.height)
    return ((hero_rect,), _partition_column(stack_rect, len(template.groups[1]), gap))


def _hero_stack_cells(rect: Rect, template: _Template, gap: int) -> tuple[tuple[Rect, ...], ...]:
    hero_height = round(rect.height * 0.58)
    stack_height = rect.height - hero_height - gap
    if template.hero_position == "bottom":
        stack_rect = Rect(rect.x, rect.y, rect.width, stack_height)
        hero_rect = Rect(rect.x, stack_rect.bottom + gap, rect.width, hero_height)
        return (_partition_row(stack_rect, len(template.groups[0]), gap), (hero_rect,))
    hero_rect = Rect(rect.x, rect.y, rect.width, hero_height)
    stack_rect = Rect(rect.x, hero_rect.bottom + gap, rect.width, stack_height)
    return ((hero_rect,), _partition_row(stack_rect, len(template.groups[1]), gap))


def _blocks_in_source_order(
    blocks: Mapping[int, BlockLayout], count: int
) -> tuple[BlockLayout, ...]:
    return tuple(blocks[index] for index in range(count))


def _resolved_label_heights(
    sources: tuple[SourceImageInfo, ...],
    label_heights: Sequence[int],
    settings: AdaptiveMosaicSettings,
) -> tuple[int, ...]:
    resolved = []
    for index, source in enumerate(sources):
        if not source.has_label:
            resolved.append(0)
            continue
        requested = label_heights[index] if index < len(label_heights) else settings.label_min_height
        resolved.append(
            max(
                settings.label_min_height,
                requested + settings.label_padding_top + settings.label_padding_bottom,
            )
        )
    return tuple(resolved)


def _content_and_footer_rect(
    canvas_size: CanvasSize, settings: AdaptiveMosaicSettings
) -> tuple[Rect, Rect | None]:
    footer = None
    content_height = canvas_size.height
    if settings.footer_height > 0:
        content_height = canvas_size.height - settings.footer_height - settings.footer_gap
        footer = Rect(0, content_height + settings.footer_gap, canvas_size.width, settings.footer_height)
    return Rect(0, 0, canvas_size.width, max(0, content_height)), footer


def _resolved_content_and_footer_rect(
    canvas_size: CanvasSize,
    settings: AdaptiveMosaicSettings,
    content_rect: Rect | None,
    footer_rect: Rect | None,
) -> tuple[Rect, Rect | None]:
    if content_rect is None:
        return _content_and_footer_rect(canvas_size, settings)
    if content_rect.width < 1 or content_rect.height < 1:
        raise ValueError("content_rect must have positive dimensions.")
    canvas_rect = Rect(0, 0, canvas_size.width, canvas_size.height)
    if not _contains(canvas_rect, content_rect):
        raise ValueError("content_rect must be inside the canvas.")
    if footer_rect is not None and not _contains(canvas_rect, footer_rect):
        raise ValueError("footer_rect must be inside the canvas.")
    return content_rect, footer_rect


def _slide_from_candidate(
    canvas_size: CanvasSize,
    candidate: MosaicCandidate,
    settings: AdaptiveMosaicSettings,
    title_rect: Rect | None = None,
    footer_rect: Rect | None = None,
) -> SlideLayout:
    _content, footer = _content_and_footer_rect(canvas_size, settings)
    if footer_rect is not None:
        footer = footer_rect
    return SlideLayout(title_rect=title_rect, blocks=candidate.blocks, footer_rect=footer)


def _justified_row_height(
    sources: tuple[SourceImageInfo, ...], row: tuple[int, ...], width: int, gap: int
) -> float:
    available_width = width - gap * (len(row) - 1)
    if available_width < len(row):
        raise ValueError("Justified row width is too small for the requested gaps.")
    ratio_sum = sum(sources[index].aspect_ratio for index in row)
    return available_width / ratio_sum


def _justified_row_rects(
    sources: tuple[SourceImageInfo, ...], row: tuple[int, ...], rect: Rect, gap: int
) -> tuple[Rect, ...]:
    raw_widths = [sources[index].aspect_ratio * rect.height for index in row]
    target_width = rect.width - gap * (len(row) - 1)
    widths = _rounded_parts(raw_widths, target_width)
    x = rect.x
    row_rects = []
    for index, width in enumerate(widths):
        row_rects.append(Rect(x, rect.y, width, rect.height))
        x += width + (gap if index < len(widths) - 1 else 0)
    return tuple(row_rects)


def _distribute_scaled(
    raw_heights: tuple[float, ...], scale: float, available_height: int, gap: int
) -> tuple[int, ...]:
    target = available_height - gap * (len(raw_heights) - 1)
    scaled = [height * scale for height in raw_heights]
    return tuple(max(1, width) for width in _rounded_parts(scaled, target))


def _rounded_parts(raw_parts: Sequence[float], target_total: int) -> tuple[int, ...]:
    floors = [int(part) for part in raw_parts]
    fractions = sorted(
        ((raw_parts[index] - floors[index], index) for index in range(len(raw_parts))),
        key=lambda item: (-item[0], item[1]),
    )
    while sum(floors) < target_total:
        for _fraction, index in fractions:
            if sum(floors) >= target_total:
                break
            floors[index] += 1
    while sum(floors) > target_total:
        changed = False
        for _fraction, index in reversed(fractions):
            if sum(floors) <= target_total:
                break
            if floors[index] <= 1:
                continue
            floors[index] = max(1, floors[index] - 1)
            changed = True
        if not changed:
            break
    return tuple(floors)


def _distribute(total: int, count: int) -> tuple[int, ...]:
    if total < count:
        raise ValueError("Cannot distribute fewer pixels than slots.")
    base = total // count
    remainder = total % count
    return tuple(base + (1 if index < remainder else 0) for index in range(count))


def _aligned_start(start: int, available: int, size: int, alignment: str) -> int:
    if alignment in {"left", "top"}:
        return start
    if alignment in {"right", "bottom"}:
        return start + available - size
    return start + round((available - size) / 2)


def _template_rank(candidate: MosaicCandidate) -> int:
    return sum(ord(character) for character in candidate.template_name)


def _areas(candidate: MosaicCandidate) -> tuple[int, ...]:
    return tuple(block.image_rect.width * block.image_rect.height for block in candidate.blocks)


def _unused_area_penalty(candidate: MosaicCandidate, content_rect: Rect) -> float:
    content_area = content_rect.width * content_rect.height
    if content_area < 1:
        return INVALID_PENALTY
    used = sum(_areas(candidate))
    return max(0.0, 100.0 * (1.0 - (used / content_area)))


def _tiny_cells_penalty(candidate: MosaicCandidate, settings: AdaptiveMosaicSettings) -> float:
    penalty = 0.0
    for block in candidate.blocks:
        width_shortfall = max(0, settings.minimum_image_width - block.image_rect.width)
        height_shortfall = max(0, settings.minimum_image_height - block.image_rect.height)
        penalty += (width_shortfall + height_shortfall) * 20.0
    return penalty


def _aspect_error_penalty(
    candidate: MosaicCandidate, sources: tuple[SourceImageInfo, ...]
) -> float:
    error = 0.0
    for block, source in zip(candidate.blocks, sources):
        if block.image_rect.width < 1 or block.image_rect.height < 1:
            error += INVALID_PENALTY
            continue
        output_ratio = block.image_rect.width / block.image_rect.height
        relative_error = abs(output_ratio - source.aspect_ratio) / source.aspect_ratio
        if relative_error > 0.03:
            error += relative_error
    return error


def _visual_imbalance_penalty(
    candidate: MosaicCandidate, settings: AdaptiveMosaicSettings
) -> float:
    areas = _areas(candidate)
    if len(areas) <= 1:
        return 0.0
    average = sum(areas) / len(areas)
    if average <= 0:
        return INVALID_PENALTY
    penalty = sum(abs(area - average) / average for area in areas) * 18.0
    if settings.hero_index is not None:
        largest_index = max(range(len(areas)), key=lambda index: areas[index])
        if largest_index != settings.hero_index:
            penalty += 5_000.0
    return penalty


def _size_difference_penalty(candidate: MosaicCandidate) -> float:
    areas = _areas(candidate)
    if not areas or min(areas) < 1:
        return INVALID_PENALTY
    return max(areas) / min(areas) * 8.0


def _label_overflow_penalty(
    candidate: MosaicCandidate, content_rect: Rect, footer_rect: Rect | None
) -> float:
    penalty = 0.0
    rects: list[Rect] = []
    for block in candidate.blocks:
        rects.append(block.image_rect)
        if block.label_rect is not None:
            if block.label_rect.y < block.image_rect.bottom:
                penalty += LABEL_OVERFLOW_PENALTY
            rects.append(block.label_rect)
    for rect in rects:
        if rect.x < content_rect.x or rect.y < content_rect.y:
            penalty += LABEL_OVERFLOW_PENALTY
        if rect.right > content_rect.right:
            penalty += LABEL_OVERFLOW_PENALTY
        if rect.bottom > content_rect.bottom:
            penalty += LABEL_OVERFLOW_PENALTY
    for left_index, left in enumerate(rects):
        for right in rects[left_index + 1 :]:
            if _intersects(left, right):
                penalty += LABEL_OVERFLOW_PENALTY
    return penalty


def _order_change_penalty(
    candidate: MosaicCandidate, settings: AdaptiveMosaicSettings
) -> float:
    if not settings.preserve_order:
        return 0.0
    expected = tuple(range(len(candidate.blocks)))
    if not candidate.source_order or candidate.source_order == expected:
        return 0.0
    inversions = 0
    for left_index, left in enumerate(candidate.source_order):
        for right in candidate.source_order[left_index + 1 :]:
            if left > right:
                inversions += 1
    return ORDER_CHANGE_PENALTY * inversions


def _edge_misalignment_penalty(candidate: MosaicCandidate, content_rect: Rect) -> float:
    edges = []
    for block in candidate.blocks:
        edges.extend(
            (
                abs(block.image_rect.x - content_rect.x),
                abs(block.image_rect.right - content_rect.right),
                abs(block.image_rect.y - content_rect.y),
                abs(block.image_rect.bottom - content_rect.bottom),
            )
        )
    close_edges = sum(1 for edge in edges if edge <= 1)
    return max(0.0, (len(candidate.blocks) * 2) - close_edges) * 3.0


def _intersects(left: Rect, right: Rect) -> bool:
    return left.x < right.right and right.x < left.right and left.y < right.bottom and right.y < left.bottom


def _contains(outer: Rect, inner: Rect) -> bool:
    return (
        inner.x >= outer.x
        and inner.y >= outer.y
        and inner.right <= outer.right
        and inner.bottom <= outer.bottom
    )


def _diagnostics(
    candidate: MosaicCandidate,
    sources: tuple[SourceImageInfo, ...],
    content_rect: Rect,
) -> dict[str, object]:
    output_ratios = tuple(
        (
            round(block.image_rect.width / block.image_rect.height, 6)
            if block.image_rect.width > 0 and block.image_rect.height > 0
            else 0.0
        )
        for block in candidate.blocks
    )
    source_ratios = tuple(round(source.aspect_ratio, 6) for source in sources)
    return {
        "template_name": candidate.template_name,
        "score": candidate.score,
        "source_aspect_ratio": source_ratios,
        "output_aspect_ratio": output_ratios,
        "unused_area_percentage": round(_unused_area_penalty(candidate, content_rect), 6),
    }
