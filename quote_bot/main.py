from io import BytesIO

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile

from .access import AccessMiddleware
from .access import public as public_command
from .settings import BotSettings
from .templates import TemplatesManager

bot = Bot(token=BotSettings.token())
dp = Dispatcher(bot, storage=MemoryStorage())
templates_manager = TemplatesManager()


@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy.pop("template")  # Reset current user template
        proxy.pop("background")
        proxy.pop("text")

    await message.answer(
        "Привет. Это бот для создания шаблонных цитат с логотипом Гражданского Общества. "
        "Отправь /templates чтобы получить список шаблонов цитат"
    )


@dp.message_handler(commands=["templates"])
async def templates_list(message: types.Message):
    templates = templates_manager.all_templates()

    for name, template in templates.items():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(f"Выбрать {name}", callback_data=name))
        await message.answer_photo(template.preview, reply_markup=keyboard)


@dp.message_handler(commands=["chat_id"])
@public_command()  # Everyone can call
async def get_chat_id(message: types.Message):
    """
    Get current chat ID (for privileges settings)
    :param message:
    :return:
    """
    await message.answer(message.chat.id)


@dp.message_handler(content_types=["text"])
async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        template = proxy.get("template", None)
        if not template or template not in templates_manager.all_templates():
            await message.answer("Сначала выберите шаблон в меню /templates")
        else:
            proxy["text"] = message.text
            await message.answer("Рисую плакат, ждите ... (до ~15 секунд)")
            png = templates_manager.process_template(template, message.text, proxy.get("background"))
            await message.answer_photo(png)
            await message.answer_document(InputFile(BytesIO(png), filename=f"{template}_poster.png"))


@dp.message_handler(content_types=[ContentType.DOCUMENT])
async def process_image(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        template = proxy.get("template")
        if not template or template not in templates_manager.all_templates():
            await message.answer("Сначала выберите шаблон в меню /templates")
            return
        if "image" not in message.document.mime_type:
            await message.answer("Это не изображение")
            return
        file = BytesIO()
        await message.document.download(file)
        proxy["background"] = file
        if not proxy.get("text"):
            await message.answer("Фон загружен. Теперь отправьте текст для цитаты.")
            return
        await message.answer("Рисую плакат, ждите ... (до ~15 секунд)")
        png = templates_manager.process_template(template, proxy["text"], proxy["background"])
        await message.answer_photo(png)
        await message.answer_document(InputFile(BytesIO(png), filename=f"{template}_poster.png"))


@dp.message_handler(content_types=[ContentType.PHOTO])
async def process_photo(message: types.Message, state: FSMContext):
    await message.answer("Отправьте это фото 'как файл' для лучшего качества")


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    template = callback_query.data
    if template not in templates_manager.all_templates():
        await bot.send_message(callback_query.from_user.id, "Такого шаблона не существует")
        return

    size = templates_manager.all_templates()[template].pil_image.size
    await bot.send_message(
        callback_query.from_user.id,
        f"Выбран шаблон {template}, теперь отправьте текст для плаката.\n\n"
        f"Чтобы указать автора цитаты, отправьте его имя после @ в формате 'Текст @ Автор'\n\n"
        f"Вы также можете отправить картинку на фон "
        f"плаката {size[0]}x{size[1]} (картинки других размеров будут растянуты/обрезаны)\n\n"
        f"Чтобы вернуться к списку шаблонов отправьте /templates",
    )
    async with state.proxy() as proxy:
        proxy["template"] = template
        proxy.pop("background")
        proxy.pop("text")


def main():
    dp.middleware.setup(AccessMiddleware(BotSettings.access_chat_id()))
    dp.loop.run_until_complete(templates_manager.update_templates())
    executor.start_polling(dp, skip_updates=True)
