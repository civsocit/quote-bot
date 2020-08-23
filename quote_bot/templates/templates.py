from copy import copy
from io import BytesIO
from math import ceil
from os import listdir, remove
from os.path import basename, dirname
from os.path import join as join_path
from os.path import realpath
from typing import Dict, Iterable, Optional, Tuple

from aiogram.types import Document
from PIL import Image, UnidentifiedImageError

from constructor_bot.designer import add_text_on_image
from constructor_bot.settings import DesignerSettings


def calculate_brightness(image) -> float:
    """
    Get image brightness
    https://gist.github.com/kmohrf/8d4653536aaa88965a69a06b81bcb022
    :param image:
    :return:
    """
    greyscale_image = image.convert("L")
    histogram = greyscale_image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale


class Template:
    def __init__(self, path: str):
        """
        Create image template
        :param path: path to .eps file
        """
        self._name = basename(path)
        self._path = path

        self._pil_image = Image.open(path)
        scale = ceil(DesignerSettings.default_width() / self._pil_image.width)
        self._pil_image.load(scale=scale)  # High resolution

        if calculate_brightness(self._pil_image) > DesignerSettings.text_brightness_threshold():
            self._text_color = DesignerSettings.text_color_dark()
        else:
            self._text_color = DesignerSettings.text_color_light()

        with BytesIO() as output:
            preview = self.pil_image
            preview.thumbnail((DesignerSettings.default_preview_width(), DesignerSettings.default_preview_width()))
            preview.save(output, format="PNG")
            self._png_preview = output.getvalue()

    @property
    def name(self) -> str:
        return self._name

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
        return self._text_color


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
        # TODO: read from backend?
        self._templates = dict()

        for path in self._template_files():
            template = Template(path)
            self._templates[template.name] = template

    async def add_template(self, tg_file: Document, caption: Optional[str] = None):
        path = join_path(self._path_to_templates, caption or tg_file.file_name)
        await tg_file.download(path)
        try:
            template = Template(path)
        except UnidentifiedImageError:
            remove(path)
            return False
        self._templates[template.name] = template
        return True

    def remove_template(self, template_name: str):
        template = self._templates.get(template_name)
        if template:
            remove(template.path)
            self._templates.pop(template_name)

    def all_templates(self) -> Dict[str, Template]:
        return self._templates

    def process_template(self, identifier: str, text: str) -> Tuple[bytes, bytes]:
        template = self._templates[identifier]
        return add_text_on_image(template.pil_image, text, template.text_color)
