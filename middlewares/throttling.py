import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for throttling command messages.

    Args:
        time_limit (int): The time limit for throttling commands in seconds.
    """
    def __init__(self, time_limit: int = 5) -> None:
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        """
        Handles the throttling of command messages.

        Args:
            handler (Callable[[Message, Dict[str, Any]], Awaitable[Any]]): The message handler function.
            event (Message): The incoming message.
            data (Dict[str, Any]): The dictionary containing data.

        Returns:
            The result of the message handler function.
        """
        if event.text.startswith('/'):  # Проверка, является ли сообщение командой
            if event.chat.id in self.limit:
                await event.reply('⛔ Слишком много запросов! ⛔')
                await asyncio.sleep(5)
                await event.reply('✅ Команда снова доступна!')
                return
            else:
                self.limit[event.chat.id] = None
        return await handler(event, data)
