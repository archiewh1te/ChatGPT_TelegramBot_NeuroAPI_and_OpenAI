from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_allusers, update_status, select_user

from filters import PrivateChatFilter, AdminFilter

from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

router = Router(name='unbans')


class Userunban(CallbackData, prefix='Userunban'):
    user_id: int


class Pagination_Unban(CallbackData, prefix="pag_unban"):
    action: str
    page: int


async def paginator_unban(session: AsyncSession, page: int = 0) -> InlineKeyboardMarkup:
    """
    Creates a pagination interface for user unban management.

    Args:
        session (AsyncSession): The async session for database operations.
        page (int): The page number for the pagination interface.

    Returns:
        InlineKeyboardMarkup: The built pagination interface.
    """
    users = await select_allusers(session=session)
    builder = InlineKeyboardBuilder()
    limit = 5
    start_offset = (page - 1) * limit
    total_pages = -(-len(users) // limit)
    end_offset = start_offset + limit
    for user in users[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(text=f'👤{user.user_id} {user.first_name}',
                                 callback_data=Userunban(user_id=user.user_id).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_Unban(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_Unban(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_Unban(action="next",
                                                                                          page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    return builder.as_markup()


# РОУТЕР ПО КНОПКЕ РАЗБАНИТЬ
@router.callback_query(F.data.startswith("unbans"), PrivateChatFilter(), AdminFilter())
async def add_unban(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the initiation of the unban process.

    Args:
        call (CallbackQuery): The callback query object.
        session (AsyncSession): The async session for database operations.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_reply_markup(reply_markup=await paginator_unban(session=session, page=1))


@router.callback_query(Pagination_Unban.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_Unban, session: AsyncSession) -> None:
    """
    Handles pagination for the unban management interface.

    Args:
        call (CallbackQuery): The callback query object.
        callback_data (Pagination_Unban): The callback data for pagination.
        session (AsyncSession): The async session for database operations.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await paginator_unban(session=session, page=page))


@router.callback_query(Userunban.filter(F.user_id), PrivateChatFilter())
async def get_unban(call: CallbackQuery, callback_data: Userunban, session: AsyncSession) -> None:
    """
    Processes the unban action for a selected user.

    Args:
        call (CallbackQuery): The callback query object.
        callback_data (Userunban): The callback data for user unban.
        session (AsyncSession): The async session for database operations.
    """
    await call.answer()
    await update_status(user_id=callback_data.user_id, session=session, status='active', commit=True)
    kb_back = InlineKeyboardBuilder()
    kb_back.row(types.InlineKeyboardButton(text='⬅Назад ', callback_data='cancel'), width=1)
    user = await select_user(session=session, user_id=callback_data.user_id)
    await call.message.edit_text(
        f"✅ Вы успешно <b>разбанили</b> пользователя <b><a href='tg://user?id={user.user_id}'>{user.first_name}</a></b>",
        reply_markup=kb_back.as_markup())
