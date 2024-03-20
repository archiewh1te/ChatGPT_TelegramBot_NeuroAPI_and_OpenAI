from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_allusers

from filters import PrivateChatFilter, AdminFilter

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

router = Router(name='all_users')


class Pagination_users(CallbackData, prefix="Pagination_users"):
    action: str
    page: int


async def paginator(session: AsyncSession, page: int = 0) -> InlineKeyboardMarkup:
    """
    Generates a paginated inline keyboard markup for displaying users.

    Args:
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
        page (int, optional): The page number. Defaults to 0.

    Returns:
        InlineKeyboardMarkup: The paginated inline keyboard markup.
    """
    users = await select_allusers(session=session)
    builder = InlineKeyboardBuilder()
    limit = 5
    start_offset = (page - 1) * limit
    total_pages = -(-len(users) // limit)
    end_offset = start_offset + limit
    for user in users[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(text=f'👤 {user.user_id} {user.first_name}',
                                 callback_data='alluser')
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_users(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_users(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_users(action="next",
                                                                                          page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))
    return builder.as_markup()


# РОУТЕР ПО КНОПКЕ ПОЛЬЗОВАТЕЛИ
@router.callback_query(F.data.startswith("users"), PrivateChatFilter(), AdminFilter())
async def get_user(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the callback query to display a list of users and pagination buttons.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    await call.answer()
    users = await select_allusers(session=session)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    banned_users_count = sum(user.status == "banned" for user in users)
    active_users_count = sum(user.status == "active" for user in users)
    await call.message.edit_text(f'📋 <b>Список пользователей:\n\n</b>'
                                 f'👥 <b>Всего пользователей:</b> {len(users)}\n'
                                 f'🚫 <b>В бане:</b> {banned_users_count}\n'
                                 f'🔈 <b>Активные:</b> {active_users_count}', reply_markup=await paginator(session=session, page=1))



@router.callback_query(Pagination_users.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_users, session: AsyncSession) -> None:
    """
    Handles the callback query to update the pagination of the user list.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination_users): The parsed callback data.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=page))
