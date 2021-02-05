from asyncio import get_event_loop
from io import BytesIO

import boto3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile

from quote_bot.access import AccessMiddleware
from quote_bot.access import public as public_command
from quote_bot.dynamo import DynamoStorage
from quote_bot.settings import BotSettings
from quote_bot.templates import TemplatesManager
from quote_bot.utils import download_file

templates_manager = TemplatesManager()


async def start(message: types.Message, state: FSMContext):
    """
    Start command handler
    """
    async with state.proxy() as proxy:
        proxy.pop("template")  # Reset current user template
        proxy.pop("background")
        proxy.pop("text")

    await message.answer(
        "Привет. Я бот для создания шаблонных цитат с логотипом Гражданского Общества. "
        "Отправь /templates чтобы получить список шаблонов цитат."
    )


async def templates_list(message: types.Message):
    """
    Get templates list command handler
    """
    templates = templates_manager.all_templates()

    for name, template in templates.items():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(f"Выбрать {name}", callback_data=name))
        await message.answer_photo(template.preview, reply_markup=keyboard)


@public_command()  # Everyone can call
async def get_chat_id(message: types.Message):
    """
    Get current chat ID (for privileges settings)
    :param message:
    :return:
    """
    await message.answer(message.chat.id)


async def _go_template(message: types.Message, proxy, template_name: str):
    """
    Process quote and background...
    """
    text = proxy["text"]
    await message.answer("Рисую плакат, ждите ... (до ~30 секунд)")
    background = await download_file(proxy.get("background"))
    png = templates_manager.process_template(template_name, text, background)
    await message.answer_photo(png)
    await message.answer_document(InputFile(BytesIO(png), filename=f"{template_name}_poster.png"))


async def process_text(message: types.Message, state: FSMContext):
    """
    Text (quote text) handler
    """
    async with state.proxy() as proxy:
        template = proxy.get("template", None)
        if not template or template not in templates_manager.all_templates():
            await message.answer("Сначала выберите шаблон в меню /templates")
        else:
            proxy["text"] = message.text
            await _go_template(message, proxy, template)


async def process_image(message: types.Message, state: FSMContext):
    """
    File (image) handler
    """
    if "image" not in message.document.mime_type:
        await message.answer("Это не изображение")
        return

    async with state.proxy() as proxy:
        template = proxy.get("template")
        if not template or template not in templates_manager.all_templates():
            await message.answer("Сначала выберите шаблон в меню /templates")
            return

        proxy["background"] = message.document.file_id

        if not proxy.get("text"):
            await message.answer("Фон загружен. Теперь отправьте текст для цитаты.")
            return

        await _go_template(message, proxy, template)


async def process_photo(message: types.Message, state: FSMContext):
    """
    Photo handler
    """
    await message.answer("Отправьте это фото 'как файл' для лучшего качества")


async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Template selection handler
    """
    bot = Bot.get_current()
    await bot.answer_callback_query(callback_query.id)
    template = callback_query.data
    if template not in templates_manager.all_templates():
        await bot.send_message(callback_query.from_user.id, "Такого шаблона не существует")
        return

    size = templates_manager.all_templates()[template].background_size
    await bot.send_message(
        callback_query.from_user.id,
        f"Выбран шаблон {template}, теперь отправьте текст для плаката.\n\n"
        f"Вы также можете отправить картинку на фон "
        f"плаката {size[0]}x{size[1]} (картинки других размеров будут растянуты/обрезаны)\n\n"
        f"Чтобы вернуться к списку шаблонов отправьте /templates",
    )
    async with state.proxy() as proxy:
        proxy["template"] = template
        proxy.pop("background")
        proxy.pop("text")


async def register_handlers(dp: Dispatcher):
    """
    Registration all handlers before processing update
    """

    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(templates_list, commands=["templates"])
    dp.register_message_handler(get_chat_id, commands=["chat_id"])
    dp.register_message_handler(process_text, content_types=["text"])
    dp.register_callback_query_handler(process_callback)
    dp.register_message_handler(process_photo, content_types=[ContentType.PHOTO])
    dp.register_message_handler(process_image, content_types=[ContentType.DOCUMENT])

    dp.middleware.setup(AccessMiddleware(BotSettings.access_chat_id()))


async def process_event(event, dp: Dispatcher):
    """
    Converting an AWS Lambda event to an update and handling that
    update
    """

    Bot.set_current(dp.bot)
    update = types.Update.to_object(event)
    await dp.process_update(update)


async def aws_main(event):
    """
    Asynchronous wrapper for initializing the bot and dispatcher,
    and launching subsequent functions
    """

    # Bot and dispatcher initialization
    bot = Bot(BotSettings.token())

    dynamodb = boto3.resource("dynamodb", region_name=BotSettings.dynamo_region())
    dp = Dispatcher(bot, storage=DynamoStorage(dynamodb))

    await register_handlers(dp)
    await process_event(event, dp)

    return "ok"


def lambda_handler(event, context):
    """
    AWS Lambda handler
    """

    return get_event_loop().run_until_complete(aws_main(event))


def main():
    """
    Classic polling
    """
    bot = Bot(BotSettings.token())
    dp = Dispatcher(bot, storage=MemoryStorage())
    get_event_loop().run_until_complete((register_handlers(dp)))
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
