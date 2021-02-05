from copy import copy
from enum import Enum
from enum import auto as enum_auto
from io import BytesIO
from os.path import dirname
from os.path import join as join_path
from os.path import realpath
from typing import Dict, Optional, Tuple

from PIL import Image

from quote_bot.designer import Align, add_background_on_image, add_text_on_image, compile_image
from quote_bot.settings import DesignerSettings
from quote_bot.textmanager import process as prepare_text


class TemplateType(Enum):
    main = enum_auto()


class Template:
    def __init__(self, path: str, _type: TemplateType):
        """
        Create image template
        :param path: path to .eps file
        """
        self._type = _type
        self._path = path

        self._pil_image = Image.open(path).convert("RGBA")

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
    def background_size(self) -> Tuple[int, int]:
        return int((1 - DesignerSettings.background_border()) * self._pil_image.width), self._pil_image.height

    @property
    def text_color(self) -> Tuple[int, int, int]:
        return {TemplateType.main: DesignerSettings.text_color_light()}[self._type]


class TemplatesManager:
    _path_to_templates: str = dirname(realpath(__file__))
    template_format: str = ".png"

    def __init__(self):
        self._templates = {
            "main": Template(join_path(self._path_to_templates, "main.png"), TemplateType.main),
        }

    def all_templates(self) -> Dict[str, Template]:
        return self._templates

    def process_template(self, identifier: str, text: str, background: Optional[BytesIO] = None) -> bytes:
        template = self._templates[identifier]

        text = prepare_text(text)

        pil_image = add_text_on_image(
            template.pil_image,
            text,
            template.text_color,
            DesignerSettings.text_position(),
            align=Align.left,
            path_to_font=DesignerSettings.path_to_font(),
        )

        if background:
            pil_image = add_background_on_image(
                pil_image, Image.open(background), int(DesignerSettings.background_border() * pil_image.width)
            )

        return compile_image(pil_image)
