import textwrap
from functools import lru_cache
from typing import Callable, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def _wrap_word(text: str, w: int) -> str:
    """
    Wrap word
    :param text: text
    :param w: max line length
    :return: Wrapped word
    """
    return "\n".join(textwrap.wrap(text, w, replace_whitespace=False, break_long_words=False))


@lru_cache()
def _font_target(
    font_size: int,
    max_width: int,
    max_height: int,
    wrapped_text: str,
    path_to_font: str,
    drawer,
    max_font: Optional[int] = None,
) -> int:
    """
    Minimize me!
    :param font_size:
    :param drawer:
    :return:
    """
    font = ImageFont.truetype(path_to_font, font_size)

    text_width, text_height = drawer.textsize(wrapped_text, font)

    if text_width > max_width or text_height > max_height:
        # Font is TOO big: minimize
        return 100000

    if max_font and font_size > max_font:
        # Font is TOO big: minimize
        return 100000

    return -font_size  # Font size must be biggest


@lru_cache()
def _wrap_target(drawer, max_width: int, max_height: int, text: str, font, max_text_len: int):
    """
    Minimize me!
    """
    dim = max_width / max_height
    wrapped = _wrap_word(text, max_text_len)
    text_width, text_height = drawer.textsize(wrapped, font)
    real_dim = text_width / text_height

    return real_dim - dim


def sign(x):
    return 1 if x >= 0 else -1


def _bisect(target: Callable[[int], int], start: int, end: int) -> int:
    """
    Integer bisect search
    find zero of TARGET (or closest to zero value)
    """
    assert end > start

    left = start
    right = end

    left_v = target(left)
    right_v = target(right)

    if left_v < 0 and right_v > 0:
        direction = 1
    elif left_v > 0 and right_v < 0:
        direction = -1
    elif left_v == 0 and right_v == 0:
        return start
    else:
        raise ValueError("Function must change sign between start and end")

    while abs(left - right) > 1:
        middle = left + int((right - left) / 2)
        val = target(middle)
        if sign(val) * direction > 0:
            right = middle
        else:
            left = middle

    if abs(target(left)) < abs(target(right)):
        return left
    else:
        return right


def optimize_font_size(
    max_width: int, max_height: int, text: str, font_path: str, max_font: Optional[int] = None
) -> Tuple[int, str]:
    """
    Optimize font size and word wrap for image
    :param max_width: maximum text width in px
    :param max_height: maximum text height in px
    :param text: text
    :param font_path: path to .ttf font file
    :param max_font: maximum font size
    :return: Tuple[font size, wrapped text (with \n symbols)]
    """
    image = Image.new("1", (max_width + 1, max_height + 1))
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, 40)

    def wrap_target(x):
        """
        Minimize me!
        :param x: max text line length
        """
        res = _wrap_target(draw, max_width, max_height, text, font, x)
        return res

    # Optimize word wrapping
    if text.count(" "):  # We don't need hyphenation if here are no tabs
        wrap = _bisect(wrap_target, 1, 200)
    else:
        wrap = 1000

    def font_target(x):
        """
        Minimize me!
        :param x: font size
        """
        res = _font_target(x, max_width, max_height, _wrap_word(text, wrap), font_path, draw, max_font)
        return res

    # Optimize font size
    font_size = _bisect(font_target, 40, 1000)

    return font_size, _wrap_word(text, wrap)
