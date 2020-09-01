from io import BytesIO
from typing import Optional

from aiocache import cached
from aiogram import Bot


@cached()
async def download_file(file_id: Optional[str] = None) -> Optional[BytesIO]:
    """
    Download file from Telegram server by ID
    Cached function
    """
    if not file_id:
        return None

    stream = BytesIO()
    bot = Bot.get_current()
    await bot.download_file_by_id(file_id, stream)
    return stream
