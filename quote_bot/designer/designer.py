import io
from enum import Enum
from enum import auto as enum_auto
from typing import Tuple
from resizeimage.resizeimage import resize_crop

from io import BytesIO

from PIL import ImageDraw, ImageFont, Image

from ..optimizator import optimize_font_size
from ..settings import DesignerSettings


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


def add_text_on_image(
    pil_image,
    text: str,
    color: Tuple[int, int, int],
    position: Tuple[float, float, float, float],
    wrap: bool = True,
    align: Align = Align.center,
):
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

    font_size, wrapped_text = optimize_font_size(
        pil_image, x1 - x0, y1 - y0, text, DesignerSettings.path_to_font(), DesignerSettings.max_font_size(), wrap
    )

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


def _resize_to_max(req_size: Tuple[int, int], image):
    if req_size[0] > image.size[0]:
        image = image.resize((req_size[0], int(req_size[0] / image.size[0] * image.size[1])))
    if req_size[1] > image.size[1]:
        image = image.resize((int(req_size[1] / image.size[1] * image.size[0]), req_size[1]))
    return image


def add_background_on_image(pil_image, background_pil):
    """
    Add background on image
    :param pil_image: PIL Image
    :param background_pil: background to add PIL Image
    :return: PIL Image
    """
    background_pil = _resize_to_max(pil_image.size, background_pil)
    background_pil = resize_crop(background_pil, pil_image.size)

    background_pil.paste(pil_image, (0, 0), pil_image)

    return background_pil


def fill_color(pil_image, color: Tuple[int, int, int]):
    """
    Add color on background
    :param pil_image: PIL Image
    :param color: color
    :return: PIL Image
    """
    background = Image.new("RGB", (pil_image.width, pil_image.height), color)
    return add_background_on_image(pil_image, background)
