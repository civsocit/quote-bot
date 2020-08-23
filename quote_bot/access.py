from enum import IntEnum

import aiogram.types as types
from aiocache import cached
from aiogram import Bot
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from constructor_bot.settings import BotSettings


class Privileges(IntEnum):
    nothing = 0
    user = 1
    admin = 2


def root_only():
    """
    Decorator for admin-only commands
    :return:
    """

    def decorator(func):
        setattr(func, "admin_only", True)
        return func

    return decorator


def public():
    """
    Decorator for public commands
    :return:
    """

    def decorator(func):
        setattr(func, "public_allowed", True)
        return func

    return decorator


@cached(ttl=BotSettings.access_cache_ttl())
async def _get_privileges(user_id: int, chat_id: int) -> Privileges:
    """
    Check user access
    :param user_id: user id
    :param chat_id: access chat id
    :return: privileges
    """
    bot = Bot.get_current()
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.is_chat_admin():
        return Privileges.admin
    if chat_member.is_chat_member():
        return Privileges.user
    return Privileges.nothing


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_chat_id: int):
        self._access_chat_id = access_chat_id
        super(AccessMiddleware, self).__init__()

    @classmethod
    def _is_root_command(cls) -> bool:
        handler = current_handler.get()
        return handler and getattr(handler, "admin_only", False)

    @classmethod
    def _is_public_command(cls) -> bool:
        handler = current_handler.get()
        return handler and getattr(handler, "public_allowed", False)

    async def on_process_message(self, message: types.Message, data: dict):
        if self._is_public_command():  # Public commands allowed
            return

        if message.chat.id < 0:  # Group chats are not allowed
            await message.answer("Для общения с ботом используйте личные сообщения")
            raise CancelHandler()

        privileges = await _get_privileges(message.from_user.id, self._access_chat_id)

        if privileges < Privileges.user:
            await message.answer("Вы должны быть участником тематического чата для доступа к Конструктору Плакатов")
            raise CancelHandler()

        if self._is_root_command() and privileges < Privileges.admin:
            await message.answer("Вы должны быть администратором чата для доступа к этому функционалу")
            raise CancelHandler()
