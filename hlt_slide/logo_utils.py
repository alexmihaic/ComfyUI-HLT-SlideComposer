"""Logo scaling, masking, and composition helpers."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageChops, ImageOps

from .config import CanvasSize, Rect


@dataclass(frozen=True)
class PreparedLogo:
    image: Image.Image
    rect: Rect


def calculate_logo_size(
    logo_image: Image.Image,
    canvas_size: CanvasSize,
    *,
    logo_width_percent: float = 18.0,
    logo_max_height_percent: float = 8.0,
) -> tuple[int, int]:
    width_percent = _clamp(logo_width_percent, 2.0, 80.0)
    height_percent = _clamp(logo_max_height_percent, 1.0, 30.0)
    max_width = max(1, round(canvas_size.width * width_percent / 100.0))
    max_height = max(1, round(canvas_size.height * height_percent / 100.0))
    scale = min(max_width / logo_image.width, max_height / logo_image.height)
    return (
        max(1, round(logo_image.width * scale)),
        max(1, round(logo_image.height * scale)),
    )


def prepare_logo(
    logo_image: Image.Image | None,
    *,
    canvas_size: CanvasSize,
    footer_rect: Rect,
    logo_mask: Image.Image | None = None,
    logo_width_percent: float = 18.0,
    logo_max_height_percent: float = 8.0,
    logo_opacity: float = 1.0,
    logo_bottom_offset: int = 0,
    invert_logo_mask: bool = True,
) -> PreparedLogo | None:
    if logo_image is None:
        return None

    size = calculate_logo_size(
        logo_image,
        canvas_size,
        logo_width_percent=logo_width_percent,
        logo_max_height_percent=logo_max_height_percent,
    )
    logo = logo_image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    logo.putalpha(_combined_alpha(logo, logo_mask, logo_opacity, invert_logo_mask))

    x = footer_rect.x + (footer_rect.width - logo.width) // 2
    centered_y = footer_rect.y + (footer_rect.height - logo.height) // 2
    y = centered_y + round(logo_bottom_offset)
    y = max(0, min(y, canvas_size.height - logo.height))
    x = max(0, min(x, canvas_size.width - logo.width))
    return PreparedLogo(logo, Rect(x, y, logo.width, logo.height))


def compose_logo(
    canvas: Image.Image,
    logo_image: Image.Image | None,
    *,
    canvas_size: CanvasSize,
    footer_rect: Rect,
    logo_mask: Image.Image | None = None,
    logo_width_percent: float = 18.0,
    logo_max_height_percent: float = 8.0,
    logo_opacity: float = 1.0,
    logo_bottom_offset: int = 0,
    invert_logo_mask: bool = True,
) -> Image.Image:
    prepared = prepare_logo(
        logo_image,
        canvas_size=canvas_size,
        footer_rect=footer_rect,
        logo_mask=logo_mask,
        logo_width_percent=logo_width_percent,
        logo_max_height_percent=logo_max_height_percent,
        logo_opacity=logo_opacity,
        logo_bottom_offset=logo_bottom_offset,
        invert_logo_mask=invert_logo_mask,
    )
    if prepared is None:
        return canvas.convert("RGB")

    base = canvas.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(prepared.image, (prepared.rect.x, prepared.rect.y), prepared.image)
    return Image.alpha_composite(base, layer).convert("RGB")


def _combined_alpha(
    logo: Image.Image,
    logo_mask: Image.Image | None,
    logo_opacity: float,
    invert_logo_mask: bool,
) -> Image.Image:
    alpha = logo.getchannel("A")
    if logo_mask is not None:
        mask = logo_mask.convert("L").resize(logo.size, Image.Resampling.LANCZOS)
        if invert_logo_mask:
            mask = ImageOps.invert(mask)
        alpha = ImageChops.multiply(alpha, mask)

    opacity = _clamp(logo_opacity, 0.0, 1.0)
    if opacity < 1.0:
        alpha = alpha.point(lambda value: round(value * opacity))
    return alpha


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))
