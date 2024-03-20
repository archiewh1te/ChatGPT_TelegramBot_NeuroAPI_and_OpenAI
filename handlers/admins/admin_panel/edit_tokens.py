from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_allusers, update_tokkens

from filters import PrivateChatFilter, AdminFilter

from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from state.send_tokens import send_to_tokens

router = Router(name='edit_tokens')


class Userdata(CallbackData, prefix='edit_tokens'):
    user_id: int


class Pagination_token(CallbackData, prefix="Pagination_token"):
    action: str
    page: int


async def paginator(session: AsyncSession, page: int = 0) -> InlineKeyboardMarkup:
    """
    Generates a paginated inline keyboard markup for displaying and navigating through user data.

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
                                 callback_data=Userdata(user_id=user.user_id).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_token(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_token(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_token(action="next",
                                                                                          page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    return builder.as_markup()


# РОУТЕР ПО КНОПКЕ ДОБАВИТЬ ПОПЫТКИ
@router.callback_query(F.data.startswith("add_attempts"), PrivateChatFilter(), AdminFilter())
async def update_token(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the callback query to display user data and options for updating token attempts.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=1))


@router.callback_query(Pagination_token.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_token, session: AsyncSession) -> None:
    """
    Handles the pagination of user data when "next" or "prev" buttons are clicked.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination_token): The parsed callback data representing the pagination action.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=page))


@router.callback_query(Userdata.filter(F.user_id), PrivateChatFilter())
async def add_token(call: CallbackQuery, callback_data: Pagination_token, state: FSMContext) -> None:
    """
    Handles the callback query to add tokens for a specific user.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination_token): The parsed callback data representing the pagination action.
        state (FSMContext): The FSMContext object to maintain state data.
    """
    await call.answer(cache_time=1)
    global msg_token
    user_id = callback_data.user_id
    kb_cancel = InlineKeyboardMarkup(row_width=2,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='❌ Отменить', callback_data='quit_token')
                                         ]
                                     ])
    msg_token = await call.message.answer(f'⚡️ Введите количество <b>токенов</b>: ', reply_markup=kb_cancel)
    await state.update_data(user_id=user_id)
    await state.set_state(send_to_tokens.text)


@router.message(PrivateChatFilter(), send_to_tokens.text)
async def get_token(message: types.Message, session: AsyncSession, state: FSMContext) -> None:
    """
    Handles the message containing the number of tokens and updates the database.

    Args:
        message (types.Message): The Message object representing the user's message.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
        state (FSMContext): The FSMContext object to maintain state data.
    """
    answer = message.text
    await state.update_data(text=answer)
    data = await state.get_data()
    user_id = data.get('user_id')
    text = data.get('text')
    await state.clear()
    await update_tokkens(user_id=user_id, session=session, tokkens=text, commit=True)
    await message.answer('✅ Вы успешно <b>добавили токены</b>.')
    await msg_token.delete()


@router.callback_query(F.data.startswith('quit_token'))
async def quit_token(call: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the callback query to cancel the token addition process and clear the state.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        state (FSMContext): The FSMContext object to maintain state data.
    """
    await state.clear()
    await call.message.delete()
    await call.message.answer('❌ Действие отменено')
