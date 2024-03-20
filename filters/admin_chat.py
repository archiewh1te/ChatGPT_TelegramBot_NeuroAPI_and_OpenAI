from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.admin_commands import select_admin_filter


class AdminFilter(BaseFilter):
    """ Filter that checks if a user is an admin. """

    async def __call__(
            self,
            obj: Union[Message, CallbackQuery],
            session: AsyncSession
    ) -> bool:

        user_id = obj.from_user.id  # Get the user ID

        is_admin = await select_admin_filter(user_id=user_id, session=session, flag='admin')
        if is_admin:
            return True
        else:
            await obj.answer('⛔️ Вы не Администратор! Данная команда не доступна ⛔️')
            return False
