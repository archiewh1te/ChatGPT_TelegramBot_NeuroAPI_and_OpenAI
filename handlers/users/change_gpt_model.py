from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from database.function.gpt_commands import select_all_gpt_model
from database.function.user_commands import update_model, select_user
from filters import PrivateChatFilter, UserBanFilter
from keyboards.users.kb_menu_user import kb_back

router = Router(name='change_gpt_model')


# РОУТЕР КНОПКИ СМЕНИТЬ МОДЕЛЬ GPT
class GPT_models(CallbackData, prefix='select_gpt_model'):
    user_id: int
    data_model: str


@router.callback_query(F.data.startswith("gptmodel"), PrivateChatFilter(), UserBanFilter())
async def get_change_gpt_model(call: CallbackQuery, session: AsyncSession):
    """
    Handles the callback for changing the GPT model.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param session: AsyncSession for database interactions.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    """
    await call.answer(cache_time=1)
    user = await select_user(user_id=call.from_user.id, session=session)
    all_models = await select_all_gpt_model(session=session)
    builder = InlineKeyboardBuilder()
    for model in all_models:
        builder.row(
            types.InlineKeyboardButton(text=f'🤖 {model.data_model} ',
                                       callback_data=GPT_models(user_id=user.user_id,
                                                                data_model=model.data_model).pack(), ),
        ),
        builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))
    await call.message.edit_text('<b>Выберите GPT модель:</b>\n\n'
                                 f'Ваша активная модель:🤖 <b>{user.gpt_model}</b>\n\n'
                                 '<i>После выбора модели вы можете задать вопрос</i>',
                                 reply_markup=builder.as_markup())
    return builder.as_markup()


# РОУТЕР ВЫБОРА МОДЕЛЕЙ
@router.callback_query(GPT_models.filter(), PrivateChatFilter(), UserBanFilter())
async def get_gpt(call: CallbackQuery, callback_data: GPT_models, session: AsyncSession) -> None:
    """
    Handles the callback for selecting GPT models.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param callback_data: The callback data representing the selected GPT model.
    :type callback_data: GPT_models
    :param session: AsyncSession for database interactions.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    """
    await update_model(user_id=callback_data.user_id, session=session, gpt_model=callback_data.data_model, commit=True)
    await call.message.edit_text(f'✅ Вы <b>успешно</b> выбрали: <b>{callback_data.data_model}</b>, теперь можно '
                                 f'задать вопрос.',
                                 reply_markup=kb_back.as_markup())
