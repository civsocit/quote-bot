import os
from os.path import abspath, dirname, join
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
        chat = os.getenv("CHAT")
        if not chat:
            raise ValueError("Access chat ID must be specified (missing .env file or CHAT environment variable?)")
        return int(chat)

    @classmethod
    def access_cache_ttl(cls) -> int:
        return 60  # in seconds

    @classmethod
    def dynamo_region(cls) -> str:
        return "us-east-1"


class DesignerSettings:
    @classmethod
    def path_to_font(cls) -> str:
        return join(abspath(dirname(__file__)), "designer", "Montserrat-SemiBold.ttf")

    @classmethod
    def text_color_light(cls) -> Tuple[int, int, int]:
        return 0xF2, 0xF2, 0xF2

    @classmethod
    def text_position(cls) -> Tuple[float, float, float, float]:
        # Relative position x0, y0, x1, y1
        return 77 / 1200, 200 / 620, 1133 / 1200, 365 / 620

    @classmethod
    def background_border(cls) -> float:
        """
                           | <- border
        ---------------------------------
        |                  |            |
        |                  |            |
        |   Some text      | Background |
        |                  |            |
        |                  |            |
        ---------------------------------
        """
        return 1048 / 1836

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
