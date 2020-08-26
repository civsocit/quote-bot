import os
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()


class BotSettings:
    @classmethod
    def token(cls) -> str:
        token = os.getenv("TOKEN")
        if not token:
            raise ValueError("Token must be specified (missing .env file or TOKEN environment variable?)")
        return token

    @classmethod
    def access_chat_id(cls) -> int:
        return -424580045

    @classmethod
    def access_cache_ttl(cls) -> int:
        return 30  # in seconds


class DesignerSettings:
    @classmethod
    def path_to_font(cls) -> str:
        from os.path import abspath, dirname, join

        return join(abspath(dirname(__file__)), "designer", "main.ttf")

    @classmethod
    def text_color_light(cls) -> Tuple[int, int, int]:
        return 0xE1, 0xE6, 0xEB

    @classmethod
    def text_color_dark(cls) -> Tuple[int, int, int]:
        return 0x19, 0x2D, 0x44

    @classmethod
    def background_color_dark(cls) -> Tuple[int, int, int]:
        return 0x00, 0x00, 0x00

    @classmethod
    def background_color_light(cls) -> Tuple[int, int, int]:
        return 0xE1, 0xE6, 0xEB

    @classmethod
    def text_position(cls) -> Tuple[float, float, float, float]:
        # Relative position x0, y0, x1, y1
        return 0.09375, 0.27777, 0.90625, 0.72222

    @classmethod
    def caption_text_position(cls) -> Tuple[float, float, float, float]:
        return 0.5 / 16, 0.5 / 9, 6 / 16, 1 / 9

    @classmethod
    def default_width(cls) -> int:
        # A3 size 16.54 inh with 200 DPI
        # Warning: Pillow uses discrete scale factor, so, 150 or 170 DPI may be equal
        return int(16.54 * 200.0)

    @classmethod
    def default_preview_width(cls) -> int:
        # A7 size 4.13 inh with 150 DPI
        return 620

    @classmethod
    def max_font_size(cls) -> int:
        return 150
