from copy import copy
from enum import Enum
from enum import auto as enum_auto
from io import BytesIO
from math import ceil
from os import listdir
from os.path import dirname
from os.path import join as join_path
from os.path import realpath
from typing import Dict, Iterable, Tuple

from PIL import Image

from quote_bot.designer import add_text_on_image
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
        scale = ceil(DesignerSettings.default_width() / self._pil_image.width)
        self._pil_image.load(scale=scale)  # High resolution

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
    def preview(self) -> bytes:
        return copy(self._png_preview)

    @property
    def text_color(self):
        return {
            TemplateType.black: DesignerSettings.text_color_dark(),
            TemplateType.white: DesignerSettings.text_color_light(),
        }[self._type]


class TemplatesManager:
    _path_to_templates: str = dirname(realpath(__file__))
    template_format: str = ".eps"

    def __init__(self):
        self._templates = dict()

    @classmethod
    def _template_files(cls) -> Iterable[str]:
        for filename in listdir(cls._path_to_templates):
            path = join_path(cls._path_to_templates, filename)
            if path.endswith(cls.template_format):
                yield path

    async def update_templates(self):
        self._templates = {
            "black": Template(join_path(self._path_to_templates, "Quot-bot-Black.eps"), TemplateType.black),
            "white": Template(join_path(self._path_to_templates, "Quot-bot-White.eps"), TemplateType.white),
        }

    def all_templates(self) -> Dict[str, Template]:
        return self._templates

    def process_template(self, identifier: str, text: str) -> Tuple[bytes, bytes]:
        template = self._templates[identifier]
        return add_text_on_image(template.pil_image, text, template.text_color)
