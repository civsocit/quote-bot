import io
from typing import Tuple

from PIL import ImageDraw, ImageFont

from ..optimizator import optimize_font_size
from ..settings import DesignerSettings


def add_text_on_image(pil_image, text: str, color: Tuple[int, int, int]) -> Tuple[bytes, bytes]:
    """
    Add text on Pillow image
    :param pil_image: Pillow image
    :param text: text to add
    :return: Tuple [PNG preview, PDF image] (files, bytes)
    """

    x0, y0, x1, y1 = DesignerSettings.text_position()
    x0, x1 = int(x0 * pil_image.width), int(x1 * pil_image.width)
    y0, y1 = int(y0 * pil_image.height), int(y1 * pil_image.height)

    font_size, wrapped_text = optimize_font_size(
        pil_image, x1 - x0, y1 - y0, text, DesignerSettings.path_to_font(), DesignerSettings.max_font_size()
    )

    # Create PIL font object
    font = ImageFont.truetype(DesignerSettings.path_to_font(), font_size)
    draw = ImageDraw.Draw(pil_image)
    text_width, text_height = draw.textsize(wrapped_text, font)

    position = (x0 + (x1 - x0 - text_width) / 2, y0 + (y1 - y0 - text_height) / 2)
    draw.text(position, wrapped_text, color, font=font, align="center")

    # Convert to bytes
    with io.BytesIO() as output:
        pil_image.save(output, format="PDF")
        pdf = output.getvalue()  # Original size

    # Convert to bytes for preview
    with io.BytesIO() as output:
        pil_image.thumbnail((DesignerSettings.default_preview_width(), DesignerSettings.default_width()))
        pil_image.save(output, format="PNG")
        preview = output.getvalue()  # PNG preview

    return preview, pdf
