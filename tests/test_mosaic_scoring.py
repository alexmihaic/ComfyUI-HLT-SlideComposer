from __future__ import annotations

import pytest

from hlt_slide.adaptive_mosaic import (
    AdaptiveMosaicSettings,
    SourceImageInfo,
    generate_mosaic_candidates,
    score_mosaic_candidate,
    select_adaptive_mosaic,
)
from hlt_slide.config import CanvasSize


def source(index: int, width: int, height: int, *, has_label: bool = True) -> SourceImageInfo:
    return SourceImageInfo(index, width, height, width / height, has_label)


def test_all_required_penalty_keys_are_reported() -> None:
    _layout, candidate = select_adaptive_mosaic(
        CanvasSize(1080, 1920),
        (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
    )

    assert set(candidate.penalties) == {
        "unused_area",
        "tiny_cells",
        "aspect_error",
        "visual_imbalance",
        "extreme_size_difference",
        "label_overflow",
        "order_change",
        "edge_misalignment",
    }
    assert candidate.penalties["aspect_error"] <= 0.001


def test_compact_strategy_penalizes_unused_area_more_than_editorial() -> None:
    sources = (source(0, 2400, 900), source(1, 900, 1600), source(2, 1000, 1000))
    candidates = generate_mosaic_candidates(CanvasSize(1080, 1920), sources)
    candidate = next(candidate for candidate in candidates if candidate.template_name == "row_3")

    compact_score = score_mosaic_candidate(
        candidate, CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(strategy="compact")
    )
    editorial_score = score_mosaic_candidate(
        candidate, CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(strategy="editorial")
    )

    assert compact_score.penalties["unused_area"] > editorial_score.penalties["unused_area"]


def test_strategies_can_choose_different_templates_for_mixed_four_images() -> None:
    sources = (
        source(0, 2400, 900),
        source(1, 900, 1600),
        source(2, 1000, 1000),
        source(3, 900, 1200),
    )

    balanced = select_adaptive_mosaic(
        CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(strategy="balanced")
    )[1]
    editorial = select_adaptive_mosaic(
        CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(strategy="editorial")
    )[1]

    assert balanced.template_name != editorial.template_name


def test_label_overflow_strongly_penalizes_candidate() -> None:
    sources = (source(0, 1600, 900), source(1, 900, 1600))
    candidates = generate_mosaic_candidates(
        CanvasSize(320, 320),
        sources,
        AdaptiveMosaicSettings(minimum_image_width=96, minimum_image_height=96),
        label_heights=(180, 180),
    )

    assert candidates
    assert any(candidate.penalties["label_overflow"] >= 1000 for candidate in candidates)


def test_order_change_penalty_applies_when_preserve_order_is_true() -> None:
    sources = (source(0, 1600, 900), source(1, 900, 1600))
    candidates = generate_mosaic_candidates(CanvasSize(1080, 1920), sources)
    swapped = next(candidate for candidate in candidates if candidate.template_name == "hero_right")

    preserve = score_mosaic_candidate(
        swapped, CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(preserve_order=True)
    )
    relaxed = score_mosaic_candidate(
        swapped, CanvasSize(1080, 1920), sources, AdaptiveMosaicSettings(preserve_order=False)
    )

    assert preserve.penalties["order_change"] > relaxed.penalties["order_change"]
