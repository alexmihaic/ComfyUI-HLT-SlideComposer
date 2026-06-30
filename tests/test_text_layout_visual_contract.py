from __future__ import annotations

from hlt_slide.config import CanvasSize
from hlt_slide.text_layouts import (
    TextLayoutSettings,
    active_text_blocks,
    describe_text_layout,
    select_text_layout,
)


def test_auto_text_comparison_geometries_are_stable() -> None:
    expected = {
        1: ("centered_statement", (118, 540, 844, 840)),
        2: ("split_2", (64, 60, 952, 888)),
        3: ("vertical_stack", (64, 60, 952, 719)),
        4: ("grid_2x2", (64, 60, 461, 888)),
    }

    for count, (effective, first_rect) in expected.items():
        blocks = active_text_blocks(
            tuple(f"Block {index}" for index in range(1, count + 1)),
            ("headline", "subheadline", "body", "caption")[:count],
        )
        layout = select_text_layout(
            CanvasSize(1080, 1920),
            blocks,
            TextLayoutSettings(),
            "auto_text",
        )

        assert layout.effective_layout == effective
        assert (
            layout.blocks[0].rect.x,
            layout.blocks[0].rect.y,
            layout.blocks[0].rect.width,
            layout.blocks[0].rect.height,
        ) == first_rect


def test_diagnostics_expose_visual_review_fields() -> None:
    blocks = active_text_blocks(("One", "Two"), ("headline", "caption"))
    layout = select_text_layout(
        CanvasSize(1920, 1080),
        blocks,
        TextLayoutSettings(split_axis="auto"),
        "split_2",
    )
    diagnostics = layout.diagnostics

    assert diagnostics.requested_layout == "split_2"
    assert diagnostics.effective_layout == "split_2"
    assert diagnostics.active_count == 2
    assert diagnostics.source_order == (0, 1)
    assert diagnostics.roles == ("headline", "caption")
    assert diagnostics.split_axis_resolved == "horizontal"
    assert 0.0 < diagnostics.content_usage_percentage <= 100.0
    assert "content_usage_percentage=" in describe_text_layout(layout)
