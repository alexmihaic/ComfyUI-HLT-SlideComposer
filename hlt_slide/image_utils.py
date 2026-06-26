"""Pure Pillow image fitting helpers."""

from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw

from .config import Rect
from .exceptions import HLTSlideError, prefixed_message


RGBA = tuple[int, int, int, int]
RGB_OR_RGBA = tuple[int, int, int] | RGBA


def fit_image_to_box(
    image: Image.Image,
    size: tuple[int, int],
    *,
    fit: str = "cover",
    crop_anchor: str = "center",
    contain_fill_mode: str = "transparent",
    cell_background_color: RGB_OR_RGBA = (17, 17, 17, 255),
    corner_radius: int = 0,
    border_width: int = 0,
    border_color: RGB_OR_RGBA = (233, 33, 36, 255),
) -> Image.Image:
    width, height = size
    if width < 1 or height < 1:
        raise HLTSlideError(prefixed_message("Target image box must be at least 1 pixel."))

    if fit == "cover":
        output = _cover(image, width, height, crop_anchor)
    elif fit == "contain":
        output = _contain(image, width, height, contain_fill_mode, cell_background_color)
    elif fit == "stretch":
        output = image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    else:
        raise HLTSlideError(prefixed_message(f"Unsupported image fit mode: {fit!r}."))

    return _apply_shape_and_border(output, corner_radius, border_width, border_color)


def compose_image_in_rect(
    canvas: Image.Image,
    image: Image.Image,
    rect: Rect,
    *,
    fit: str = "cover",
    crop_anchor: str = "center",
    contain_fill_mode: str = "transparent",
    cell_background_color: RGB_OR_RGBA = (17, 17, 17, 255),
    corner_radius: int = 0,
    border_width: int = 0,
    border_color: RGB_OR_RGBA = (233, 33, 36, 255),
) -> Image.Image:
    result = canvas.copy()
    fitted = fit_image_to_box(
        image,
        (rect.width, rect.height),
        fit=fit,
        crop_anchor=crop_anchor,
        contain_fill_mode=contain_fill_mode,
        cell_background_color=cell_background_color,
        corner_radius=corner_radius,
        border_width=border_width,
        border_color=border_color,
    )
    if fitted.mode == "RGBA":
        composited = result.convert("RGBA")
        composited.alpha_composite(fitted, (rect.x, rect.y))
        result = composited.convert(result.mode)
    else:
        result.paste(fitted, (rect.x, rect.y))
    return result


def _cover(image: Image.Image, width: int, height: int, crop_anchor: str) -> Image.Image:
    source = image.convert("RGB")
    scale = max(width / source.width, height / source.height)
    resized_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    resized = source.resize(resized_size, Image.Resampling.LANCZOS)

    left = max(0, (resized.width - width) // 2)
    top = _crop_top(resized.height, height, crop_anchor)
    return resized.crop((left, top, left + width, top + height))


def _contain(
    image: Image.Image,
    width: int,
    height: int,
    contain_fill_mode: str,
    cell_background_color: RGB_OR_RGBA,
) -> Image.Image:
    if contain_fill_mode not in {"transparent", "cell_color"}:
        raise HLTSlideError(
            prefixed_message(f"Unsupported contain fill mode: {contain_fill_mode!r}.")
        )

    source = image.convert("RGBA" if "A" in image.getbands() else "RGB")
    scale = min(width / source.width, height / source.height)
    resized_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    resized = source.resize(resized_size, Image.Resampling.LANCZOS)
    if contain_fill_mode == "transparent":
        background = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    else:
        background = Image.new("RGB", (width, height), cell_background_color[:3])
    offset = ((width - resized.width) // 2, (height - resized.height) // 2)
    if resized.mode == "RGBA" and background.mode == "RGBA":
        background.alpha_composite(resized, offset)
    elif resized.mode == "RGBA":
        composited = background.convert("RGBA")
        composited.alpha_composite(resized, offset)
        background = composited.convert("RGB")
    else:
        background.paste(resized, offset)
    return background


def _crop_top(resized_height: int, target_height: int, crop_anchor: str) -> int:
    extra = max(0, resized_height - target_height)
    if crop_anchor == "top":
        return 0
    if crop_anchor == "center":
        return extra // 2
    if crop_anchor == "bottom":
        return extra
    raise HLTSlideError(
        prefixed_message(f"Unsupported crop anchor: {crop_anchor!r}.")
    )


def _apply_shape_and_border(
    image: Image.Image,
    corner_radius: int,
    border_width: int,
    border_color: RGB_OR_RGBA,
) -> Image.Image:
    if corner_radius <= 0 and border_width <= 0:
        return image

    output = image.convert("RGBA")
    radius = max(0, min(corner_radius, min(output.size) // 2))
    if corner_radius > 0:
        mask = Image.new("L", output.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(
            (0, 0, output.width - 1, output.height - 1),
            radius=radius,
            fill=255,
        )
        output.putalpha(ImageChops.multiply(output.getchannel("A"), mask))
        clean_output = Image.new("RGBA", output.size, (0, 0, 0, 0))
        clean_output.alpha_composite(output)
        output = clean_output

    if border_width > 0:
        draw = ImageDraw.Draw(output)
        inset = border_width // 2
        draw.rounded_rectangle(
            (inset, inset, output.width - 1 - inset, output.height - 1 - inset),
            radius=max(0, radius - inset),
            outline=border_color,
            width=border_width,
        )
    return output
