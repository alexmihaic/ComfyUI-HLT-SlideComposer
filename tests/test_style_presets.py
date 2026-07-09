from __future__ import annotations

from hlt_slide.renderer import (
    STYLE_PRESET_NAMES,
    apply_style_preset,
    RenderSettings,
)


def test_custom_style_preset_does_not_change_settings() -> None:
    settings = RenderSettings(
        background_color="#123456",
        title_color="#ABCDEF",
        label_color="#FEDCBA",
        outer_margin=12,
    )

    assert apply_style_preset(settings, "custom") == settings


def test_unknown_style_preset_falls_back_to_custom_safely() -> None:
    settings = RenderSettings(background_color="#123456")

    assert apply_style_preset(settings, "unknown") == settings


def test_style_preset_names_are_stable_for_node_selector() -> None:
    assert STYLE_PRESET_NAMES == (
        "custom",
        "hlt_editorial_red",
        "hlt_dark_review",
        "hlt_clean_portfolio",
        "hlt_poster_bold",
    )


def test_hlt_editorial_red_returns_hlt_defaults_and_editorial_spacing() -> None:
    styled = apply_style_preset(RenderSettings(), "hlt_editorial_red")

    assert styled.background_color == "#000000"
    assert styled.title_color == "#E92124"
    assert styled.label_color == "#E92124"
    assert styled.cell_background_color == "#111111"
    assert styled.outer_margin > RenderSettings().outer_margin
    assert styled.corner_radius > RenderSettings().corner_radius


def test_hlt_dark_review_uses_discreet_labels_and_compact_cells() -> None:
    styled = apply_style_preset(RenderSettings(), "hlt_dark_review")

    assert styled.background_color == "#0B0D10"
    assert styled.label_color == "#B7BBC2"
    assert styled.cell_background_color == "#15181D"
    assert styled.label_font_size < RenderSettings().label_font_size
    assert styled.block_gap < RenderSettings().block_gap


def test_hlt_clean_portfolio_uses_light_background_and_wide_margins() -> None:
    styled = apply_style_preset(RenderSettings(), "hlt_clean_portfolio")

    assert styled.background_color == "#F3F0E8"
    assert styled.title_color == "#161616"
    assert styled.label_color == "#303030"
    assert styled.cell_background_color == "#FFFFFF"
    assert styled.outer_margin > RenderSettings().outer_margin


def test_hlt_poster_bold_uses_larger_title_and_more_air() -> None:
    styled = apply_style_preset(RenderSettings(), "hlt_poster_bold")

    assert styled.background_color == "#000000"
    assert styled.title_color == "#E92124"
    assert styled.title_font_size > RenderSettings().title_font_size
    assert styled.title_gap > RenderSettings().title_gap
    assert styled.corner_radius > RenderSettings().corner_radius


def test_style_preset_does_not_override_existing_custom_controls() -> None:
    settings = RenderSettings(
        background_color="#223344",
        title_color="#445566",
        outer_margin=10,
        corner_radius=0,
    )

    styled = apply_style_preset(settings, "hlt_clean_portfolio")

    assert styled.background_color == "#223344"
    assert styled.title_color == "#445566"
    assert styled.outer_margin == 10
    assert styled.corner_radius == 0
    assert styled.label_color == "#303030"
