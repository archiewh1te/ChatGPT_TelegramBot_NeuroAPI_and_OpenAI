from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from database.function.gpt_commands import delete_gpt_model, select_all_gpt_model
from filters import PrivateChatFilter, UserBanFilter

router = Router(name='delete_model')


# РОУТЕР КНОПКИ СМЕНИТЬ МОДЕЛЬ GPT
class GPT_models_del(CallbackData, prefix='del_model'):
    gpt_id: int
    data_model: str


@router.callback_query(F.data.startswith("delete_model_gpt"), PrivateChatFilter(), UserBanFilter())
async def get_change_gpt_model(call: CallbackQuery, session: AsyncSession):
    """
    Handles the callback query to display a list of GPT models and provide options for deleting a model.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    await call.answer(cache_time=1)
    all_models = await select_all_gpt_model(session=session)
    builder = InlineKeyboardBuilder()
    for model in all_models:
        builder.row(
            types.InlineKeyboardButton(text=f'🤖 {model.data_model}',
                                       callback_data=GPT_models_del(gpt_id=model.gpt_id,
                                                                    data_model=model.data_model).pack(), ),
        ),
        builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    await call.message.edit_text('<b>Выберите <b>GPT модель</b> чтобы удалить:</b>\n',
                                 reply_markup=builder.as_markup())
    return builder.as_markup()


# РОУТЕР ВЫБОРА МОДЕЛЕЙ
@router.callback_query(GPT_models_del.filter(), PrivateChatFilter(), UserBanFilter())
async def get_gpt(call: CallbackQuery, callback_data: GPT_models_del, session: AsyncSession) -> None:
    """
    Handles the callback query to delete a specific GPT model and display the result.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (GPT_models_del): The parsed callback data representing the GPT model to delete.
        session (AsyncSession): The AsyncSession object for asynchronous database operations.
    """
    await delete_gpt_model(gpt_id=callback_data.gpt_id, session=session, commit=True)
    kb_back = InlineKeyboardBuilder()
    kb_back.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='edit'))
    await call.message.edit_text(f'✅ Вы <b>успешно</b> удалили: <b>{callback_data.data_model}</b>.',
                                 reply_markup=kb_back.as_markup())
