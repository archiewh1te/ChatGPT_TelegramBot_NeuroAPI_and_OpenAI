from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware for adding database session to data dictionary.

    Args:
        session_pool: The pool for creating database sessions.
    """
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """
        Adds a database session to the data dictionary and calls the handler.

        Args:
            handler: The handler function to be called.
            event: The TelegramObject representing the event.
            data: The dictionary containing data.

        Returns:
            The result of the handler function.
        """
        async with self.session_pool() as session:
            data['session'] = session
            result = await handler(event, data)
        return result