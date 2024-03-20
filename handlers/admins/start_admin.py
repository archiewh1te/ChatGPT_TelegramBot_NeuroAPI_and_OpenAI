from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.admin_commands import create_admin
from filters import PrivateChatFilter

from aiogram import Router
from aiogram.types import Message

router = Router(name='add_admin')


# ---------------------------------БЛОК РЕГИСТРАЦИИ АДМИНИСТРАТОРОВ-----------------------------------------------------
@router.message(Command('odminreg'), PrivateChatFilter())
async def admins_add(message: Message, session: AsyncSession) -> None:
    """
    Handles the 'odminreg' command for adding administrators.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    """
    await create_admin(session=session, user_id=message.from_user.id,
                       first_name=message.from_user.first_name,
                       last_name=message.from_user.last_name,
                       user_name=message.from_user.username,
                       status='active',
                       flag='admin', commit=True)
    await message.answer('✅Доступ разрешен, используйте команду /panelodm')



