from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for adding configuration data to data dictionary.

    Args:
        config: The configuration data.
    """
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """
        Adds configuration data to data dictionary and calls the handler.

        Args:
            handler: The handler function to be called.
            event: The TelegramObject representing the event.
            data: The dictionary containing data.

        Returns:
            The result of the handler function.
        """
        data['config'] = self.config
        return await handler(event, data)