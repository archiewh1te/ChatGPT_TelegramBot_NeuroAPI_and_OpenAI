from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_allusers, update_subscription

from filters import PrivateChatFilter, AdminFilter

from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from state.send_subscription import send_to_subscription

router = Router(name='subscription')


class Users_subscript(CallbackData, prefix='subscript'):
    user_id: int


class Pagination_subs(CallbackData, prefix="Pagination_subs"):
    action: str
    page: int


async def paginator(session: AsyncSession, page: int = 0) -> InlineKeyboardMarkup:
    """
    Creates a pagination interface for user subscription management.

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
            InlineKeyboardButton(text=f'👤 {user.user_id} {user.first_name}',
                                 callback_data=Users_subscript(user_id=user.user_id).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_subs(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_subs(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_subs(action="next",
                                                                                         page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    return builder.as_markup()


# РОУТЕР ПО КНОПКЕ ИЗМЕНИТЬ СТАТУС ПОДПИСКИ
@router.callback_query(F.data.startswith("subscription"), PrivateChatFilter(), AdminFilter())
async def start_subscription(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the start of subscription management for admin.

    Args:
        call (CallbackQuery): The callback query object.
        session (AsyncSession): The async session for database operations.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=1))


@router.callback_query(Pagination_subs.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_subs, session: AsyncSession) -> None:
    """
    Handles pagination for the subscription management interface.

    Args:
        call (CallbackQuery): The callback query object.
        callback_data (Pagination_subs): The callback data for pagination.
        session (AsyncSession): The async session for database operations.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await paginator(session=session, page=page))


@router.callback_query(Users_subscript.filter(F.user_id), PrivateChatFilter())
async def add_subscription(call: CallbackQuery, callback_data: Users_subscript, state: FSMContext) -> None:
    """
    Handles the addition of a user to the subscription list.

    Args:
        call (CallbackQuery): The callback query object.
        callback_data (Users_subscript): The callback data for user subscription.
        state (FSMContext): The state context.
    """
    await call.answer()
    user_id = callback_data.user_id
    kb_cancel = InlineKeyboardMarkup(row_width=2,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='❌ Отменить', callback_data='quit_subscription')
                                         ]
                                     ])
    msg_status = await call.message.answer(f'Введите статус подписки: ', reply_markup=kb_cancel)
    await state.update_data(user_id=user_id, msg_status=msg_status)
    await state.set_state(send_to_subscription.text)


@router.message(PrivateChatFilter(), send_to_subscription.text)
async def get_subscription(message: types.Message, session: AsyncSession, state: FSMContext) -> None:
    """
    Gets the subscription details and updates the user's subscription status.

    Args:
        message (types.Message): The message object received from the user.
        session (AsyncSession): The async session for database operations.
        state (FSMContext): The state context for the subscription process.
    """
    answer = message.text
    await state.update_data(text=answer)
    data = await state.get_data()
    user_id = data.get('user_id')
    msg_status = data.get('msg_status')
    await msg_status.delete()
    text = data.get('text')
    await state.clear()
    await update_subscription(user_id=user_id, session=session, subscription=text, commit=True)
    await message.answer('✅ Вы успешно добавили попытки')


@router.callback_query(F.data.startswith('quit_subscription'))
async def quit_subscription(call: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the cancellation of the subscription action.

    Args:
        call (CallbackQuery): The callback query object.
        state (FSMContext): The state context for the subscription process.
    """
    await state.clear()
    await call.message.delete()
    await call.message.answer('❌ Действие отменено')
