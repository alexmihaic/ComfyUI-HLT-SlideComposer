from __future__ import annotations

import pytest

from hlt_slide.adaptive_mosaic import SourceImageInfo, build_justified_rows
from hlt_slide.config import Rect


def source(index: int, width: int, height: int) -> SourceImageInfo:
    return SourceImageInfo(index, width, height, width / height, True)


def test_justified_row_uses_shared_height_and_preserves_order() -> None:
    rows = build_justified_rows(
        (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
        ((0, 1, 2),),
        Rect(0, 0, 900, 600),
        gap=24,
    )

    assert len(rows) == 1
    rects = rows[0]
    assert tuple(rect.x for rect in rects) == (0, rects[1].x, rects[2].x)
    assert len({rect.height for rect in rects}) == 1
    assert rects[0].x < rects[1].x < rects[2].x
    assert rects[-1].right == 900
    assert rects[1].x - rects[0].right == 24
    assert rects[2].x - rects[1].right == 24


@pytest.mark.parametrize("split", [((0,), (1, 2, 3)), ((0, 1), (2, 3)), ((0, 1, 2), (3,))])
def test_justified_splits_fit_available_area(split: tuple[tuple[int, ...], ...]) -> None:
    sources = (
        source(0, 1600, 900),
        source(1, 900, 1600),
        source(2, 1000, 1000),
        source(3, 900, 1200),
    )

    rows = build_justified_rows(sources, split, Rect(20, 30, 760, 900), gap=20)

    flattened = [rect for row in rows for rect in row]
    assert len(flattened) == 4
    assert all(rect.x >= 20 for rect in flattened)
    assert all(rect.y >= 30 for rect in flattened)
    assert all(rect.right <= 780 for rect in flattened)
    assert all(rect.bottom <= 930 for rect in flattened)
    assert [rect for row in rows for rect in row] == flattened


def test_justified_rows_distribute_rounding_error_deterministically() -> None:
    sources = (source(0, 333, 200), source(1, 777, 500), source(2, 555, 400))

    first = build_justified_rows(sources, ((0, 1, 2),), Rect(0, 0, 1001, 500), gap=17)
    second = build_justified_rows(sources, ((0, 1, 2),), Rect(0, 0, 1001, 500), gap=17)

    assert first == second
    assert first[0][-1].right == 1001


def test_justified_rows_reject_impossible_minimum_width() -> None:
    with pytest.raises(ValueError, match="minimum"):
        build_justified_rows(
            (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
            ((0, 1, 2),),
            Rect(0, 0, 220, 300),
            gap=24,
            minimum_image_width=96,
        )
