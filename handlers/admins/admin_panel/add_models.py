import asyncio

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.function.gpt_commands import create_gpt_model, count_gpt_model
from filters import PrivateChatFilter, AdminFilter
from state.create_gpt_model import gpt_model

router = Router(name='add_gpt_models')


# --------------------------------- БЛОК ДОБАВЛЕНИЯ МОДЕЛИ ГПТ В БД ----------------------------------------------------

@router.callback_query(F.data.startswith("create_model_gpt"), PrivateChatFilter(), AdminFilter())
async def add_gpt_model(call: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик добавления новой модели GPT.

    Args:
        call: types.CallbackQuery - The CallbackQuery object triggering the handler.
        state: FSMContext - The state of the current conversation.

    Returns:
        None
    """
    kb_cancel = InlineKeyboardMarkup(row_width=1,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='❌ Отменить', callback_data='quit_model')
                                         ]
                                     ])
    await call.answer(cache_time=1)
    global msg_name

    msg_name = await call.message.answer('Введите <b>название</b> модели:\n', reply_markup=kb_cancel)

    await state.set_state(gpt_model.name)


@router.message(PrivateChatFilter(), gpt_model.name)
async def name_model(message: types.Message, session: AsyncSession, state: FSMContext) -> None:
    """
    Обработчик ввода название модели GPT.

    Args:
        message: types.Message - The Message object triggering the handler.
        state: FSMContext - The state of the current conversation.
        session: AsyncSession - The asynchronous session to work with the database.

    Returns:
        None
    """
    await state.update_data(name=message.text)
    data = await state.get_data()
    name_model_gpt = data.get('name')
    count_id_model = await count_gpt_model(session=session)

    if count_id_model is not None:
        next_gpt_id = count_id_model + 1
    else:
        next_gpt_id = 1

    await create_gpt_model(session=session, gpt_id=next_gpt_id, data_model=name_model_gpt, commit=True)

    await message.answer(f'✅ Вы успешно <b>Добавили</b> модель GPT <b>{name_model_gpt}</b> !')
    await state.clear()

    # Удаление сообщений после того как изменили Фамилию пользователю через 1 секунду
    await asyncio.sleep(1)
    await msg_name.delete()


@router.callback_query(F.data.startswith('quit_model'))
async def quit_model(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer('❌ Действие отменено')
