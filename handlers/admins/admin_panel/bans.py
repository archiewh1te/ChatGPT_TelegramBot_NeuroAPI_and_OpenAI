from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_allusers, update_status, select_user

from filters import PrivateChatFilter, AdminFilter

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

router = Router(name='bans')


class Userban(CallbackData, prefix='ban'):
    users_id: int


class Pagination(CallbackData, prefix="pag"):
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
                                 callback_data=Userban(users_id=user.user_id).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next",
                                                                                    page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    return builder.as_markup()


# РОУТЕР ПО КНОПКЕ ЗАБАНИТЬ
@router.callback_query(F.data.startswith("bans"), PrivateChatFilter(), AdminFilter())
async def add_ban(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the callback query to display a list of users and pagination buttons for adding a ban.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=1))


@router.callback_query(Pagination.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination, session: AsyncSession) -> None:
    """
    Handles the callback query to update the pagination of the user list for adding a ban.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination): The parsed callback data.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=page))


@router.callback_query(Userban.filter(), PrivateChatFilter())
async def get_ban(call: CallbackQuery, callback_data: Userban, session: AsyncSession) -> None:
    """
    Handles the callback query to add a ban to a user and display the result.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Userban): The parsed callback data representing the user's ID.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    # Обновляем статус пользователя и показываем результат
    await update_status(user_id=callback_data.users_id, session=session, status='banned', commit=True)
    kb_back = InlineKeyboardBuilder()
    kb_back.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))
    user = await select_user(session=session, user_id=callback_data.users_id)
    await call.message.edit_text(
        f"✅ Вы успешно <b>забанили</b> пользователя <b><a href='tg://user?id={user.user_id}'>{user.first_name}</a></b>",
        reply_markup=kb_back.as_markup())
