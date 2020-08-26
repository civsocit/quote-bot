from copy import copy
from enum import Enum
from enum import auto as enum_auto
from io import BytesIO
from os.path import dirname
from os.path import join as join_path
from os.path import realpath
from typing import Dict, Optional, Tuple

from PIL import Image

from quote_bot.designer import Align, add_text_on_image, compile_image, add_background_on_image, fill_color
from quote_bot.settings import DesignerSettings


class TemplateType(Enum):
    black = enum_auto()
    white = enum_auto()


class Template:
    def __init__(self, path: str, _type: TemplateType):
        """
        Create image template
        :param path: path to .eps file
        """
        self._type = _type
        self._path = path

        self._pil_image = Image.open(path)

        with BytesIO() as output:
            preview = self.pil_image
            preview.thumbnail((DesignerSettings.default_preview_width(), DesignerSettings.default_preview_width()))
            preview.save(output, format="PNG")
            self._png_preview = output.getvalue()

    @property
    def name(self) -> str:
        return self._type.name

    @property
    def path(self) -> str:
        return self._path

    @property
    def pil_image(self):
        return copy(self._pil_image)

    @property
    def size(self):
        return self._pil_image.size

    @property
    def preview(self) -> bytes:
        return copy(self._png_preview)

    @property
    def text_color(self) -> Tuple[int, int, int]:
        return {
            TemplateType.black: DesignerSettings.text_color_light(),
            TemplateType.white: DesignerSettings.text_color_dark(),
        }[self._type]

    @property
    def background_color(self) -> Tuple[int, int, int]:
        return {
            TemplateType.black: DesignerSettings.background_color_dark(),
            TemplateType.white: DesignerSettings.background_color_light()
        }[self._type]


class TemplatesManager:
    _path_to_templates: str = dirname(realpath(__file__))
    template_format: str = ".png"

    def __init__(self):
        self._templates = dict()

    async def update_templates(self):
        self._templates = {
            "black": Template(join_path(self._path_to_templates, "Quot-bot-285.png"), TemplateType.black),
            "white": Template(join_path(self._path_to_templates, "Quot-bot-185.png"), TemplateType.white),
        }

    def all_templates(self) -> Dict[str, Template]:
        return self._templates

    def process_template(self, identifier: str, text: str, background: Optional[BytesIO] = None) -> bytes:
        template = self._templates[identifier]

        if "@" in text:
            text, caption = text.split("@", maxsplit=1)
        else:
            caption = ""
        text = text.strip()
        caption = caption.strip()

        pil_image = add_text_on_image(template.pil_image, text, template.text_color, DesignerSettings.text_position())

        if caption:
            pil_image = add_text_on_image(
                pil_image, caption, template.text_color, DesignerSettings.caption_text_position(), align=Align.left
            )

        if background:
            pil_image = add_background_on_image(pil_image, Image.open(background))
        else:
            pil_image = fill_color(pil_image, template.background_color)

        return compile_image(pil_image)
