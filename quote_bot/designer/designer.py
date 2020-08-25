import io
from typing import Tuple

from PIL import ImageDraw, ImageFont

from ..optimizator import optimize_font_size
from ..settings import DesignerSettings

from enum import Enum, auto as enum_auto


class Align(Enum):
    left = enum_auto()
    center = enum_auto()


def compile_image(pil_image) -> bytes:
    """
    Convert Pillow image to telegram image
    """
    # Convert to bytes
    with io.BytesIO() as output:
        pil_image.save(output, format="PNG")
        png = output.getvalue()
    return png


def process_text(pil_image, text: str, color: Tuple[int, int, int]):
    """
    Add text and caption on Pillow image
    :param pil_image: Pillow image
    :param text: text to add
    :param color: text color RGB
    :return: PIL Image
    """
    if "@" in text:
        text, caption = text.split("@", 2)
    else:
        caption = ""
    text = text.strip()
    caption = caption.strip()

    pil_image = add_text_on_image(pil_image, text, color, DesignerSettings.text_position())

    if caption:
        pil_image = add_text_on_image(pil_image, caption, color, DesignerSettings.caption_text_position(),
                                      align=Align.left)

    return pil_image


def add_text_on_image(pil_image, text: str, color: Tuple[int, int, int], position: Tuple[float, float, float, float],
                      wrap: bool = True,
                      align: Align = Align.center):
    """
    Add text on Pillow image
    :param pil_image: Pillow image
    :param text: text to add
    :param color: text color RGB
    :param position: text position (relative coordinates like 0.3, 0.3, 0.8, 0.8)
    :param wrap: wrap text (default - True)
    :param align: text align
    :return: Pillow image
    """

    x0, y0, x1, y1 = position
    x0, x1 = int(x0 * pil_image.width), int(x1 * pil_image.width)
    y0, y1 = int(y0 * pil_image.height), int(y1 * pil_image.height)

    font_size, wrapped_text = optimize_font_size(pil_image, x1 - x0, y1 - y0, text,
                                                 DesignerSettings.path_to_font(),
                                                 DesignerSettings.max_font_size(),
                                                 wrap)

    # Create PIL font object
    font = ImageFont.truetype(DesignerSettings.path_to_font(), font_size)
    draw = ImageDraw.Draw(pil_image)
    text_width, text_height = draw.textsize(wrapped_text, font)

    if align is Align.center:
        position = (x0 + (x1 - x0 - text_width) / 2, y0 + (y1 - y0 - text_height) / 2)
    elif align is Align.left:
        position = x0, y0
    draw.text(position, wrapped_text, color, font=font, align=align.name)

    return pil_image
