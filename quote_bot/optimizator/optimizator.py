import textwrap
from functools import lru_cache
from typing import Tuple

import numpy as np
from PIL import ImageDraw, ImageFont
from scipy.optimize import minimize


def _vec_to_val(x) -> Tuple[int, int]:
    """
    Convert optimizator x[...] vector to font size and word wrap max length
    :param x: numpy array
    :return: Tuple [font size, word wrap max length]
    """
    # +1 because x may be 0
    return abs(int(x[0])) + 1, abs(int(x[1])) + 1


def _wrap_word(text: str, w: int) -> str:
    """
    Wrap word
    :param text: text
    :param w: max line length
    :return: Wrapped word
    """
    return "\n".join(textwrap.wrap(text, w, replace_whitespace=False, break_long_words=False))


@lru_cache()
def _target(
    font_size: int, max_text_len: int, max_width: int, max_height: int, text: str, path_to_font: str, drawer
) -> int:
    """
    Minimize me!
    :param font_size:
    :param max_text_len:
    :param drawer:
    :return:
    """
    wrapped = _wrap_word(text, max_text_len)
    font = ImageFont.truetype(path_to_font, font_size)

    text_width, text_height = drawer.textsize(wrapped, font)

    if text_width > max_width or text_height > max_height:
        # Font is TOO big: minimize
        return max(text_width - max_width, 0) + max(text_height - max_height, 0)

    return -font_size  # Font size must be biggest


def optimize_font_size(image, max_width: int, max_height: int, text: str, font_path: str) -> Tuple[int, str]:
    """
    Optimize font size and word wrap for image
    :param image: PIL Image
    :param max_width: maximum text width in px
    :param max_height: maximum text height in px
    :param text: text
    :param font_path: path to .ttf font file
    :return: Tuple[font size, wrapped text (with \n symbols)]
    """
    draw = ImageDraw.Draw(image)

    def target(x):
        """
        Minimize me!
        :param x: [font size, word wrap value]
        :return: - font size (maximize font size)
        """
        font_size, max_text_len = _vec_to_val(x)

        res = _target(font_size, max_text_len, max_width, max_height, text, font_path, draw)
        return res

    # x[0] - font size, x[1] - word wrap max phrase length
    # For better optimization, try different initial values
    best = min(
        minimize(target, np.array([1, 5]), method="powell"),
        minimize(target, np.array([1, 15]), method="powell"),
        minimize(target, np.array([1, 25]), method="powell"),
        key=lambda x: x.fun,
    )
    font_size, max_text_len = _vec_to_val(best.x)
    return font_size, _wrap_word(text, max_text_len)
